"""Patient routes — Care Companion module.

Handles: bill upload/OCR, discharge translation/audio, health checks, claim tracking.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import Optional
from datetime import datetime
from bson import ObjectId
import os

from middleware.auth_middleware import require_role, get_current_user
from database import get_db
from models.health_check import HealthCheckCreate
from services.ocr_service import extract_bill_items
from services.llm_service import analyze_bill, simplify_discharge_summary
from services.translation_service import translate_and_speak, get_supported_languages
from services.rag_service import index_policy_pdf

router = APIRouter()

patient_role = require_role(["patient"])


@router.post("/upload-bill")
async def upload_hospital_bill(
    file: UploadFile = File(...),
    current_user: dict = Depends(patient_role),
):
    """Upload hospital bill image → OCR extracts line items → LLM analyzes charges.

    Returns structured bill breakdown with coverage analysis.
    """
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/jpg", "image/tiff", "application/pdf"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Upload a bill image (JPEG/PNG) or PDF")

    # Save uploaded file
    os.makedirs("uploads/bills", exist_ok=True)
    file_path = f"uploads/bills/{current_user['id']}_{file.filename}"
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Step 1: OCR extract text and parse line items
    bill_data = await extract_bill_items(file_path)

    if bill_data.get("error"):
        raise HTTPException(status_code=400, detail=bill_data["error"])

    # Step 2: LLM analyzes which charges are covered
    policy_info = ""
    if current_user.get("policy_number"):
        policy_info = f"Policy: {current_user['policy_number']}, Insurer: {current_user.get('insurer_name', 'Unknown')}"

    analysis = await analyze_bill(bill_data["items"], policy_info)

    # Save bill analysis to MongoDB
    db = get_db()
    bill_doc = {
        "patient_id": current_user["id"],
        "patient_name": current_user["full_name"],
        "file_path": file_path,
        "raw_text": bill_data["raw_text"],
        "ocr_items": bill_data["items"],
        "llm_analysis": analysis,
        "created_at": datetime.utcnow(),
    }
    result = await db.bill_analyses.insert_one(bill_doc)

    return {
        "id": str(result.inserted_id),
        "raw_text": bill_data["raw_text"],
        "items": bill_data["items"],
        "analysis": analysis,
    }


@router.post("/translate-discharge")
async def translate_discharge_summary(
    summary_text: str = Form(...),
    target_language: str = Form("hi"),
    current_user: dict = Depends(patient_role),
):
    """Translate discharge summary to vernacular language and generate audio MP3.

    1. LLM simplifies medical jargon to plain language
    2. deep-translator translates to target language (Hindi, Bengali, etc.)
    3. gTTS generates downloadable MP3 audio
    """
    # Step 1: Simplify the discharge summary
    simplified = await simplify_discharge_summary(summary_text)

    # Step 2: Translate and generate audio
    result = await translate_and_speak(simplified, target_language)

    # Save to MongoDB
    db = get_db()
    doc = {
        "patient_id": current_user["id"],
        "original_text": summary_text,
        "simplified_text": simplified,
        **result,
        "created_at": datetime.utcnow(),
    }
    await db.discharge_translations.insert_one(doc)

    return {
        "original_text": summary_text,
        "simplified_text": simplified,
        **result,
    }


@router.get("/languages")
async def list_languages():
    """Get supported languages for discharge summary translation."""
    return get_supported_languages()


@router.post("/health-check")
async def submit_health_check(
    check_data: HealthCheckCreate,
    current_user: dict = Depends(patient_role),
):
    """Submit daily post-discharge health check.

    Auto-flags concerning answers and notifies the assigned doctor.
    """
    db = get_db()

    # Find patient's most recent doctor (from latest clinical note)
    latest_note = await db.clinical_notes.find_one(
        {"patient_id": current_user["id"]},
        sort=[("created_at", -1)],
    )
    doctor_id = latest_note["doctor_id"] if latest_note else "unassigned"

    # Auto-flag logic: check for concerning symptoms
    is_flagged, flag_reasons = _evaluate_health_check(check_data)

    check_doc = {
        "patient_id": current_user["id"],
        "patient_name": current_user["full_name"],
        "doctor_id": doctor_id,
        "wound_condition": check_data.wound_condition,
        "fever": check_data.fever,
        "temperature": check_data.temperature,
        "pain_level": check_data.pain_level,
        "appetite": check_data.appetite,
        "mobility": check_data.mobility,
        "medication_taken": check_data.medication_taken,
        "additional_notes": check_data.additional_notes,
        "is_flagged": is_flagged,
        "flag_reasons": flag_reasons,
        "doctor_notified": is_flagged,  # Auto-notify if flagged
        "created_at": datetime.utcnow(),
    }

    result = await db.health_checks.insert_one(check_doc)

    return {
        "id": str(result.inserted_id),
        "is_flagged": is_flagged,
        "flag_reasons": flag_reasons,
        "message": "Health check submitted. Your doctor has been notified." if is_flagged
                   else "Health check submitted. Everything looks good!",
    }


@router.get("/health-checks")
async def get_health_check_history(current_user: dict = Depends(patient_role)):
    """Get patient's health check history."""
    db = get_db()
    checks = await db.health_checks.find(
        {"patient_id": current_user["id"]}
    ).sort("created_at", -1).to_list(30)

    for check in checks:
        check["id"] = str(check["_id"])
        del check["_id"]

    return checks


@router.get("/claims")
async def get_my_claims(current_user: dict = Depends(patient_role)):
    """Get patient's insurance claim status with plain-language explanations."""
    db = get_db()
    claims = await db.claims.find(
        {"patient_id": current_user["id"]}
    ).sort("submitted_at", -1).to_list(50)

    for claim in claims:
        claim["id"] = str(claim["_id"])
        del claim["_id"]
        # Add plain-language status explanation
        claim["status_explanation"] = _explain_claim_status(claim)

    return claims


@router.get("/bill-analyses")
async def get_bill_analyses(current_user: dict = Depends(patient_role)):
    """Get patient's past bill analyses."""
    db = get_db()
    bills = await db.bill_analyses.find(
        {"patient_id": current_user["id"]}
    ).sort("created_at", -1).to_list(20)

    for bill in bills:
        bill["id"] = str(bill["_id"])
        del bill["_id"]

    return bills


def _evaluate_health_check(check: HealthCheckCreate) -> tuple:
    """Evaluate health check answers and flag concerning symptoms.

    Returns (is_flagged: bool, flag_reasons: list).
    """
    flags = []

    # Wound concerns
    if check.wound_condition in ("discharge", "bleeding"):
        flags.append(f"Wound condition: {check.wound_condition} — needs immediate attention")
    elif check.wound_condition in ("red", "swollen"):
        flags.append(f"Wound condition: {check.wound_condition} — possible infection")

    # Fever
    if check.fever:
        flags.append("Patient reports fever")
    if check.temperature and check.temperature >= 38.5:
        flags.append(f"High temperature: {check.temperature}°C")

    # Pain
    if check.pain_level >= 7:
        flags.append(f"Severe pain level: {check.pain_level}/10")
    elif check.pain_level >= 5:
        flags.append(f"Moderate pain level: {check.pain_level}/10")

    # Appetite and mobility
    if check.appetite == "none":
        flags.append("No appetite — possible complication")
    if check.mobility == "bedridden":
        flags.append("Patient is bedridden — may need follow-up")

    # Medication compliance
    if not check.medication_taken:
        flags.append("Patient has NOT taken prescribed medication")

    # Flag if 2+ concerning indicators, or any severe one
    severe_flags = [f for f in flags if "immediate" in f or "bleeding" in f or "Severe" in f or "High temp" in f]
    is_flagged = len(flags) >= 2 or len(severe_flags) > 0

    return is_flagged, flags


def _explain_claim_status(claim: dict) -> str:
    """Generate plain-language explanation of claim status."""
    status = claim.get("status", "pending")
    amount = claim.get("total_amount", 0)
    approved = claim.get("approved_amount")

    explanations = {
        "pending": f"Your claim for Rs {amount:,.0f} is being reviewed. This usually takes 1-2 business days.",
        "approved": f"Great news! Your claim has been approved for Rs {approved or amount:,.0f}."
                    + (f" (Original claim: Rs {amount:,.0f})" if approved and approved < amount else ""),
        "rejected": f"Your claim for Rs {amount:,.0f} was not approved. Reason: {claim.get('rejection_reason', 'Contact your insurer for details')}.",
        "flagged": f"Your claim for Rs {amount:,.0f} needs additional review. Reason: {claim.get('adjudication_notes', 'Under manual review')}.",
    }

    return explanations.get(status, "Status unknown. Please contact your insurer.")


@router.post("/upload-policy")
async def upload_my_policy(
    file: UploadFile = File(...),
    insurer_name: str = Form(...),
    current_user: dict = Depends(patient_role),
):
    """Patient uploads their own insurance policy PDF.

    Indexes it in ChromaDB and links the policy_id to the patient's profile.
    Doctor never needs to upload — it's auto-fetched during consultation.
    """
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    os.makedirs("uploads/policies", exist_ok=True)
    file_path = f"uploads/policies/{current_user['id']}_{file.filename}"
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Use patient_id as the unique policy_id so doctor can auto-fetch it
    policy_id = f"patient_{current_user['id']}"
    result = await index_policy_pdf(file_path, policy_id, insurer_name)

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    db = get_db()
    # Save to policy_documents collection
    await db.policy_documents.update_one(
        {"policy_id": policy_id},
        {"$set": {
            "policy_id": policy_id,
            "patient_id": current_user["id"],
            "insurer_name": insurer_name,
            "file_path": file_path,
            "uploaded_at": datetime.utcnow(),
            **result,
        }},
        upsert=True,
    )
    # Link policy_id to patient's user record
    await db.users.update_one(
        {"_id": ObjectId(current_user["id"])},
        {"$set": {"policy_id": policy_id, "insurer_name": insurer_name}},
    )

    return {"message": "Policy uploaded successfully", "policy_id": policy_id, **result}


@router.get("/my-policy")
async def get_my_policy(current_user: dict = Depends(patient_role)):
    """Get current patient's uploaded policy info."""
    db = get_db()
    policy_id = f"patient_{current_user['id']}"
    doc = await db.policy_documents.find_one({"policy_id": policy_id})
    if not doc:
        return {"has_policy": False}
    return {
        "has_policy": True,
        "insurer_name": doc.get("insurer_name"),
        "uploaded_at": doc.get("uploaded_at"),
        "policy_id": policy_id,
    }
