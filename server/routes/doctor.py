"""Doctor routes — Smart Scribe module.

Handles: speech transcript processing, LLM clinical note structuring,
RAG policy upload/check, FHIR JSON generation, claim submission.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import Optional
from datetime import datetime
from bson import ObjectId
import os
import json

from middleware.auth_middleware import require_role, get_current_user
from database import get_db
from models.clinical_note import ClinicalNoteCreate, ClinicalNoteResponse, Prescription
from models.claim import ClaimCreate, ClaimItem
from services.llm_service import structure_clinical_note, check_policy_coverage
from services.rag_service import index_policy_pdf, check_medication_coverage, query_policy

router = APIRouter()

doctor_role = require_role(["doctor"])


@router.post("/structure-note")
async def structure_transcript(
    transcript: str = Form(...),
    patient_id: str = Form(...),
    patient_name: str = Form(...),
    policy_id: Optional[str] = Form(None),
    current_user: dict = Depends(doctor_role),
):
    """Process speech-to-text transcript through LLM to create structured clinical note.

    1. LLM parses transcript into symptoms, diagnosis, prescriptions
    2. If policy_id provided, RAG checks each prescription against policy
    3. Returns structured note with coverage warnings
    """
    db = get_db()

    structured = await structure_clinical_note(transcript)

    policy_warnings = []
    prescriptions = []

    for rx in structured.get("prescriptions", []):
        prescription = Prescription(
            medication=rx.get("medication") or "",
            dosage=rx.get("dosage") or "",
            frequency=rx.get("frequency") or "",
            duration=rx.get("duration") or "",
            is_new=rx.get("is_new"),
            stopped=rx.get("stopped"),
        )

        if policy_id:
            coverage = await check_medication_coverage(policy_id, prescription.medication)
            prescription.is_covered = coverage.get("is_covered", False)
            prescription.alternative = coverage.get("alternative")

            if not prescription.is_covered:
                warning = f"⚠ {prescription.medication} is NOT covered. "
                if prescription.alternative:
                    warning += f"Switch to {prescription.alternative} for claim approval."
                else:
                    warning += "Patient will need to pay out-of-pocket."
                policy_warnings.append(warning)

        prescriptions.append(prescription)

    fhir_encounter = _build_fhir_encounter(
        doctor=current_user,
        patient_id=patient_id,
        patient_name=patient_name,
        structured=structured,
        prescriptions=prescriptions,
    )

    note_doc = {
        "doctor_id": current_user["id"],
        "doctor_name": current_user["full_name"],
        "patient_id": patient_id,
        "patient_name": patient_name,
        "raw_transcript": transcript,
        "symptoms": structured.get("symptoms", []),
        "diagnosis": structured.get("diagnosis", ""),
        "prescriptions": [rx.dict() for rx in prescriptions],
        "icd_codes": structured.get("icd_codes", []),
        "notes": structured.get("notes", ""),
        "recommended_tests": structured.get("recommended_tests", []),
        "safety_flags": structured.get("safety_flags", []),
        "fhir_encounter": fhir_encounter,
        "policy_warnings": policy_warnings,
        "created_at": datetime.utcnow(),
    }

    result = await db.clinical_notes.insert_one(note_doc)

    return {
        "id": str(result.inserted_id),
        **note_doc,
        "_id": None,
    }


@router.post("/upload-policy")
async def upload_policy_pdf(
    file: UploadFile = File(...),
    policy_id: str = Form(...),
    insurer_name: str = Form(...),
    current_user: dict = Depends(doctor_role),
):
    """Upload insurance policy PDF for RAG indexing.

    Extracts text with PyPDF2, chunks it, stores in ChromaDB for policy-aware consultations.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    os.makedirs("uploads/policies", exist_ok=True)
    file_path = f"uploads/policies/{policy_id}_{file.filename}"

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    result = await index_policy_pdf(file_path, policy_id, insurer_name)

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    db = get_db()
    await db.policy_documents.update_one(
        {"policy_id": policy_id},
        {"$set": {
            "policy_id": policy_id,
            "insurer_name": insurer_name,
            "file_path": file_path,
            "uploaded_by": current_user["id"],
            "indexed_at": datetime.utcnow(),
            **result,
        }},
        upsert=True,
    )

    return {"message": "Policy indexed successfully", **result}


@router.get("/clinical-notes")
async def list_clinical_notes(current_user: dict = Depends(doctor_role)):
    """Get all clinical notes created by the current doctor."""
    db = get_db()
    notes = await db.clinical_notes.find(
        {"doctor_id": current_user["id"]}
    ).sort("created_at", -1).to_list(100)

    for note in notes:
        note["id"] = str(note["_id"])
        del note["_id"]

    return notes


@router.get("/clinical-notes/{note_id}")
async def get_clinical_note(note_id: str, current_user: dict = Depends(doctor_role)):
    """Get a specific clinical note."""
    db = get_db()
    note = await db.clinical_notes.find_one({"_id": ObjectId(note_id), "doctor_id": current_user["id"]})
    if not note:
        raise HTTPException(status_code=404, detail="Clinical note not found")
    note["id"] = str(note["_id"])
    del note["_id"]
    return note


@router.get("/patients")
async def list_patients(current_user: dict = Depends(doctor_role)):
    """List all patients (for doctor to select during consultation)."""
    db = get_db()
    patients = await db.users.find(
        {"role": "patient"},
        {"hashed_password": 0}
    ).to_list(100)

    for p in patients:
        p["id"] = str(p["_id"])
        del p["_id"]
        p["policy_id"] = f"patient_{p['id']}"

    return patients


@router.post("/submit-claim")
async def submit_claim(claim_data: ClaimCreate, current_user: dict = Depends(doctor_role)):
    """Submit an insurance claim from a clinical note to the insurer."""
    db = get_db()

    claim_doc = {
        "doctor_id": current_user["id"],
        "doctor_name": current_user["full_name"],
        "patient_id": claim_data.patient_id,
        "patient_name": claim_data.patient_name,
        "policy_number": claim_data.policy_number,
        "insurer_name": claim_data.insurer_name,
        "clinical_note_id": claim_data.clinical_note_id,
        "diagnosis": claim_data.diagnosis,
        "icd_codes": claim_data.icd_codes,
        "items": [item.dict() for item in claim_data.items],
        "total_amount": claim_data.total_amount,
        "room_type": claim_data.room_type,
        "status": "pending",
        "adjudication_notes": None,
        "rejection_reason": None,
        "flag_reasons": [],
        "approved_amount": None,
        "submitted_at": datetime.utcnow(),
        "adjudicated_at": None,
    }

    result = await db.claims.insert_one(claim_doc)

    return {"id": str(result.inserted_id), "message": "Claim submitted successfully", "status": "pending"}


@router.get("/flagged-health-checks")
async def get_flagged_health_checks(current_user: dict = Depends(doctor_role)):
    """Get health checks flagged for doctor attention."""
    db = get_db()
    checks = await db.health_checks.find(
        {"doctor_id": current_user["id"], "is_flagged": True}
    ).sort("created_at", -1).to_list(50)

    for check in checks:
        check["id"] = str(check["_id"])
        del check["_id"]

    return checks


def _build_fhir_encounter(doctor, patient_id, patient_name, structured, prescriptions):
    """Build a FHIR-compliant Encounter resource JSON."""
    return {
        "resourceType": "Encounter",
        "status": "finished",
        "class": {"code": "AMB", "display": "ambulatory"},
        "subject": {
            "reference": f"Patient/{patient_id}",
            "display": patient_name,
        },
        "participant": [{
            "individual": {
                "reference": f"Practitioner/{doctor['id']}",
                "display": doctor["full_name"],
            }
        }],
        "diagnosis": [{
            "condition": {"display": structured.get("diagnosis", "")},
            "rank": 1,
        }],
        "reasonCode": [{"text": s} for s in structured.get("symptoms", [])],
        "period": {
            "start": datetime.utcnow().isoformat(),
            "end": datetime.utcnow().isoformat(),
        },
        "extension": [{
            "url": "medications",
            "valueString": json.dumps([rx.dict() for rx in prescriptions]),
        }],
    }
