"""Hospital Admin routes — manages patient records, billing, and claim submission.

Flow: Doctor writes note → Hospital Admin adds billing → submits to Insurer.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import Optional
from datetime import datetime, timezone
from bson import ObjectId
import os

from middleware.auth_middleware import require_role
from database import get_db
from models.claim import ClaimItem, HospitalClaimCreate, MedicationSubstitution
from services.rag_service import index_policy_pdf, query_policy
from services.llm_service import check_policy_coverage

router = APIRouter()
hospital_role = require_role(["hospital"])

ROOM_RATES = {
    "general": 1500,
    "semi-private": 3000,
    "private": 6000,
    "icu": 12000,
}


@router.get("/dashboard-stats")
async def dashboard_stats(current_user: dict = Depends(hospital_role)):
    db = get_db()

    # All patients in the system
    admitted = await db.users.count_documents({"role": "patient"})

    # Notes that have no matching claim yet
    all_notes = await db.clinical_notes.find({}, {"_id": 1}).to_list(500)
    all_note_ids = [str(n["_id"]) for n in all_notes]
    claimed_note_ids = await db.claims.distinct("clinical_note_id")
    pending_billing = len(set(all_note_ids) - set(claimed_note_ids))

    # Claims submitted by this hospital today
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    submitted_today = await db.claims.count_documents({
        "hospital_id": current_user["id"],
        "submitted_at": {"$gte": today},
    })

    return {
        "admitted_patients": admitted,
        "notes_pending_billing": pending_billing,
        "claims_submitted_today": submitted_today,
    }


@router.get("/patients")
async def list_patients(current_user: dict = Depends(hospital_role)):
    """All patients with their latest clinical note and policy info."""
    db = get_db()
    patients = await db.users.find(
        {"role": "patient"}, {"hashed_password": 0}
    ).to_list(100)

    result = []
    for p in patients:
        p["id"] = str(p["_id"])
        del p["_id"]

        # Latest clinical note for this patient
        note = await db.clinical_notes.find_one(
            {"patient_id": p["id"]},
            sort=[("created_at", -1)]
        )
        if note:
            note["id"] = str(note["_id"])
            del note["_id"]
            p["latest_note"] = note
        else:
            p["latest_note"] = None

        # Check if policy is uploaded
        policy = await db.policy_documents.find_one({"patient_id": p["id"]})
        p["has_policy"] = bool(policy)
        result.append(p)

    return result


@router.get("/clinical-notes")
async def list_all_notes(current_user: dict = Depends(hospital_role)):
    """All clinical notes across all doctors — hospital sees everything."""
    db = get_db()

    # Find notes not yet billed
    claimed_note_ids = await db.claims.distinct("clinical_note_id")
    notes = await db.clinical_notes.find(
        {}
    ).sort("created_at", -1).to_list(200)

    for note in notes:
        note["id"] = str(note["_id"])
        del note["_id"]
        note["already_billed"] = note["id"] in claimed_note_ids

    return notes


@router.get("/clinical-notes/{note_id}")
async def get_note(note_id: str, current_user: dict = Depends(hospital_role)):
    db = get_db()
    note = await db.clinical_notes.find_one({"_id": ObjectId(note_id)})
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    note["id"] = str(note["_id"])
    del note["_id"]
    return note


@router.post("/submit-claim")
async def submit_claim(
    claim: HospitalClaimCreate,
    current_user: dict = Depends(hospital_role),
):
    """Hospital admin finalises billing and submits claim to insurer."""
    db = get_db()

    # Fetch the clinical note to build medication line items
    note = await db.clinical_notes.find_one({"_id": ObjectId(claim.clinical_note_id)})
    if not note:
        raise HTTPException(status_code=404, detail="Clinical note not found")

    # Build substitution lookup from hospital's accepted swaps
    sub_map = {s.original: s.replacement for s in claim.medication_substitutions}

    # Build items from prescriptions, applying substitutions where accepted
    items = []
    for rx in note.get("prescriptions", []):
        original_name = rx.get("medication", "Medication")
        med_name = sub_map.get(original_name, original_name)
        label = med_name if med_name == original_name else f"{med_name} (substituted for {original_name})"
        items.append({
            "description": label,
            "icd_code": None,
            "amount": 150.0,
            "category": "medication",
        })

    # Add consultation fee
    items.insert(0, {
        "description": "Doctor Consultation Fee",
        "icd_code": claim.icd_codes[0] if claim.icd_codes else None,
        "amount": 600.0,
        "category": "consultation",
    })

    # Add room charges
    room_rate = claim.room_charge_per_day or ROOM_RATES.get(claim.room_type or "general", 1500)
    days = claim.room_days or 1
    if claim.room_type:
        items.append({
            "description": f"Room Charges ({claim.room_type.title()}, {days} day{'s' if days > 1 else ''})",
            "icd_code": None,
            "amount": room_rate * days,
            "category": "room",
        })

    # Add extra charges from hospital admin
    for extra in claim.extra_charges:
        items.append(extra.dict())

    total = sum(i["amount"] for i in items)

    claim_doc = {
        "hospital_id": current_user["id"],
        "hospital_name": current_user.get("hospital_name", current_user["full_name"]),
        "submitted_by": "hospital",
        "doctor_id": note.get("doctor_id"),
        "doctor_name": note.get("doctor_name"),
        "patient_id": claim.patient_id,
        "patient_name": claim.patient_name,
        "policy_number": claim.policy_number,
        "insurer_name": claim.insurer_name,
        "clinical_note_id": claim.clinical_note_id,
        "diagnosis": claim.diagnosis,
        "icd_codes": claim.icd_codes,
        "items": items,
        "total_amount": total,
        "room_type": claim.room_type,
        "status": "pending",
        "adjudication_notes": None,
        "rejection_reason": None,
        "flag_reasons": [],
        "approved_amount": None,
        "submitted_at": datetime.now(timezone.utc),
        "adjudicated_at": None,
    }

    result = await db.claims.insert_one(claim_doc)
    return {"message": "Claim submitted successfully", "claim_id": str(result.inserted_id), "total_amount": total}


@router.post("/check-medication-coverage")
async def check_medication_coverage(
    body: dict,
    current_user: dict = Depends(hospital_role),
):
    """Check insurance coverage for each medication in a clinical note.

    For excluded drugs, suggests the closest therapeutically equivalent drug
    that IS covered under the patient's policy.
    """
    db = get_db()
    patient_id = body.get("patient_id")
    note_id = body.get("note_id")

    if not patient_id or not note_id:
        raise HTTPException(status_code=400, detail="patient_id and note_id are required")

    # Get patient's policy
    policy_doc = await db.policy_documents.find_one({"patient_id": patient_id})
    if not policy_doc:
        raise HTTPException(status_code=404, detail="No insurance policy found for this patient. Upload one first.")

    policy_id = policy_doc["policy_id"]
    insurer_name = policy_doc.get("insurer_name", "Unknown Insurer")

    # Get the clinical note
    note = await db.clinical_notes.find_one({"_id": ObjectId(note_id)})
    if not note:
        raise HTTPException(status_code=404, detail="Clinical note not found")

    prescriptions = note.get("prescriptions", [])
    if not prescriptions:
        return {"policy_id": policy_id, "insurer_name": insurer_name, "results": []}

    # Check each medication against the policy via RAG + LLM
    results = []
    for rx in prescriptions:
        med_name = rx.get("medication") or rx.get("drug") or rx.get("name", "Unknown")

        # RAG: fetch relevant policy sections for this drug
        policy_context = await query_policy(
            policy_id,
            f"coverage for {med_name} drug formulary excluded medications covered medicines"
        )

        # LLM: interpret coverage + suggest alternative if excluded
        coverage = await check_policy_coverage(med_name, policy_context)

        results.append({
            "medication": med_name,
            "dosage": rx.get("dosage", ""),
            "frequency": rx.get("frequency", ""),
            "duration": rx.get("duration", ""),
            "is_covered": coverage.get("is_covered", False),
            "reason": coverage.get("reason", ""),
            "alternative": coverage.get("alternative"),
            "alt_reason": coverage.get("alt_reason"),
        })

    return {
        "policy_id": policy_id,
        "insurer_name": insurer_name,
        "results": results,
    }


@router.post("/daily-bill/check-coverage")
async def check_item_coverage_for_bill(
    body: dict,
    current_user: dict = Depends(hospital_role),
):
    """Real-time coverage check for a single daily bill item."""
    db = get_db()
    patient_id = body.get("patient_id")
    description = body.get("description", "")
    category = body.get("category", "other")

    policy_doc = await db.policy_documents.find_one({"patient_id": patient_id})
    if not policy_doc:
        raise HTTPException(
            status_code=404,
            detail="No insurance policy found for this patient. Upload the policy PDF first.",
        )

    # ALL items go through RAG + LLM — no guessing, no keyword shortcuts
    policy_context = await query_policy(
        policy_doc["policy_id"],
        f"coverage for {description} drug formulary excluded medications covered items procedures",
    )

    if not policy_context:
        raise HTTPException(
            status_code=400,
            detail="Policy exists but could not be read from the index. Please re-upload the policy PDF.",
        )

    return await check_policy_coverage(description, policy_context)


@router.post("/daily-bill")
async def create_daily_bill(
    body: dict,
    current_user: dict = Depends(hospital_role),
):
    """Save a daily bill with per-item coverage already resolved."""
    db = get_db()
    patient_id = body.get("patient_id")
    items = body.get("items", [])

    patient = await db.users.find_one({"_id": ObjectId(patient_id)})
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    insurer_items = [i for i in items if i.get("is_covered")]
    patient_items = [i for i in items if not i.get("is_covered")]
    insurer_total = sum(float(i.get("amount", 0)) for i in insurer_items)
    patient_total = sum(float(i.get("amount", 0)) for i in patient_items)

    bill_doc = {
        "hospital_id": current_user["id"],
        "hospital_name": current_user.get("full_name"),
        "patient_id": patient_id,
        "patient_name": patient.get("full_name"),
        "policy_number": patient.get("policy_number") or body.get("policy_number"),
        "insurer_name": patient.get("insurer_name") or body.get("insurer_name"),
        "bill_date": body.get("bill_date", datetime.now(timezone.utc).date().isoformat()),
        "items": items,
        "insurer_items": insurer_items,
        "patient_items": patient_items,
        "insurer_total": insurer_total,
        "patient_total": patient_total,
        "total_amount": insurer_total + patient_total,
        "status": "draft",
        "claim_id": None,
        "created_at": datetime.now(timezone.utc),
        "submitted_at": None,
    }

    result = await db.daily_bills.insert_one(bill_doc)
    return {
        "id": str(result.inserted_id),
        "insurer_total": insurer_total,
        "patient_total": patient_total,
        "total_amount": insurer_total + patient_total,
    }


@router.post("/daily-bill/{bill_id}/submit")
async def submit_daily_bill(
    bill_id: str,
    current_user: dict = Depends(hospital_role),
):
    """Submit only the covered items as an itemized claim to the insurer."""
    db = get_db()
    bill = await db.daily_bills.find_one({"_id": ObjectId(bill_id)})
    if not bill:
        raise HTTPException(status_code=404, detail="Daily bill not found")
    if bill.get("status") == "submitted":
        raise HTTPException(status_code=400, detail="Bill already submitted")

    insurer_items = bill.get("insurer_items", [])
    if not insurer_items:
        raise HTTPException(status_code=400, detail="No covered items to submit to insurer")

    claim_doc = {
        "hospital_id": current_user["id"],
        "hospital_name": current_user.get("full_name"),
        "submitted_by": "hospital",
        "patient_id": bill["patient_id"],
        "patient_name": bill["patient_name"],
        "policy_number": bill.get("policy_number"),
        "insurer_name": bill.get("insurer_name"),
        "clinical_note_id": None,
        "diagnosis": f"Daily Bill — {bill.get('bill_date')}",
        "icd_codes": [],
        "items": [
            {"description": i["description"], "icd_code": None, "amount": float(i["amount"]), "category": i.get("category", "other")}
            for i in insurer_items
        ],
        "total_amount": bill["insurer_total"],
        "room_type": None,
        "status": "pending",
        "adjudication_notes": None,
        "rejection_reason": None,
        "flag_reasons": [],
        "approved_amount": None,
        "submitted_at": datetime.now(timezone.utc),
        "adjudicated_at": None,
        "daily_bill_id": str(bill["_id"]),
    }

    claim_result = await db.claims.insert_one(claim_doc)
    claim_id = str(claim_result.inserted_id)

    await db.daily_bills.update_one(
        {"_id": ObjectId(bill_id)},
        {"$set": {"status": "submitted", "claim_id": claim_id, "submitted_at": datetime.now(timezone.utc)}},
    )

    return {
        "claim_id": claim_id,
        "insurer_total": bill["insurer_total"],
        "patient_total": bill["patient_total"],
        "patient_items": bill.get("patient_items", []),
    }


@router.post("/upload-policy")
async def upload_policy_for_patient(
    file: UploadFile = File(...),
    patient_id: str = Form(...),
    insurer_name: str = Form(...),
    current_user: dict = Depends(hospital_role),
):
    """Hospital reception uploads patient's insurance policy PDF."""
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    db = get_db()
    patient = await db.users.find_one({"_id": ObjectId(patient_id), "role": "patient"})
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    os.makedirs("uploads/policies", exist_ok=True)
    file_path = f"uploads/policies/{patient_id}_{file.filename}"
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    policy_id = f"patient_{patient_id}"
    result = await index_policy_pdf(file_path, policy_id, insurer_name)

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    await db.policy_documents.update_one(
        {"policy_id": policy_id},
        {"$set": {
            "policy_id": policy_id,
            "patient_id": patient_id,
            "insurer_name": insurer_name,
            "file_path": file_path,
            "uploaded_by": current_user["id"],
            "uploaded_at": datetime.now(timezone.utc),
            **result,
        }},
        upsert=True,
    )
    await db.users.update_one(
        {"_id": ObjectId(patient_id)},
        {"$set": {"policy_id": policy_id, "insurer_name": insurer_name}},
    )

    return {"message": f"Policy uploaded for {patient['full_name']}", "policy_id": policy_id}
