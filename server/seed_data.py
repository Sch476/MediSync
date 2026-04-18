"""Seed script — populates MongoDB with demo data so the app works out of the box.

Run: python seed_data.py
Requires: MONGODB_URI in .env or environment variable
"""
import asyncio
import os
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/medisync")
DB_NAME = "medisync"


async def seed():
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[DB_NAME]

    # Clear existing data
    for collection in ["users", "clinical_notes", "claims", "health_checks", "policy_documents", "bill_analyses"]:
        await db[collection].drop()

    print("Cleared existing data.")

    # ── Users ──
    hashed_pw = pwd_context.hash("password123")

    doctor = {
        "email": "doctor@demo.com",
        "hashed_password": hashed_pw,
        "full_name": "Test Doctor",
        "role": "doctor",
        "license_number": "MCI-2019-78432",
        "specialization": "General Medicine",
        "policy_number": None,
        "insurer_name": None,
        "created_at": datetime.utcnow(),
    }

    insurer = {
        "email": "insurer@demo.com",
        "hashed_password": hashed_pw,
        "full_name": "Test Insurance",
        "role": "insurer",
        "license_number": None,
        "specialization": None,
        "policy_number": None,
        "insurer_name": "Star Health Insurance",
        "created_at": datetime.utcnow(),
    }

    patient1 = {
        "email": "patient@demo.com",
        "hashed_password": hashed_pw,
        "full_name": "P1",
        "role": "patient",
        "license_number": None,
        "specialization": None,
        "policy_number": "STD-78901",
        "insurer_name": "Star Health Insurance",
        "created_at": datetime.utcnow(),
    }

    patient2 = {
        "email": "patient2@demo.com",
        "hashed_password": hashed_pw,
        "full_name": "P2",
        "role": "patient",
        "license_number": None,
        "specialization": None,
        "policy_number": "STD-45678",
        "insurer_name": "HDFC Ergo",
        "created_at": datetime.utcnow(),
    }

    users = await db.users.insert_many([doctor, insurer, patient1, patient2])
    doctor_id = str(users.inserted_ids[0])
    insurer_id = str(users.inserted_ids[1])
    patient1_id = str(users.inserted_ids[2])
    patient2_id = str(users.inserted_ids[3])

    print(f"Created 4 users: doctor, insurer, 2 patients")

    # ── Clinical Notes ──
    notes = [
        {
            "doctor_id": doctor_id,
            "doctor_name": "Test Doctor",
            "patient_id": patient1_id,
            "patient_name": "P1",
            "raw_transcript": "Patient complains of fever for 3 days, cough with yellowish sputum, and body aches. Temperature 101F. Chest clear on auscultation. Prescribing Paracetamol 500mg TDS for 5 days and Azithromycin 500mg OD for 3 days.",
            "symptoms": ["fever", "cough with yellowish sputum", "body aches"],
            "diagnosis": "Acute Upper Respiratory Infection",
            "prescriptions": [
                {"medication": "Paracetamol 500mg", "dosage": "1 tablet", "frequency": "3 times daily", "duration": "5 days", "is_covered": True, "alternative": None},
                {"medication": "Azithromycin 500mg", "dosage": "1 tablet", "frequency": "once daily", "duration": "3 days", "is_covered": True, "alternative": None},
                {"medication": "Cetirizine 10mg", "dosage": "1 tablet", "frequency": "at bedtime", "duration": "5 days", "is_covered": True, "alternative": None},
            ],
            "icd_codes": ["J06.9"],
            "notes": "Patient advised rest and hydration. Follow-up in 5 days if symptoms persist.",
            "fhir_encounter": {"resourceType": "Encounter", "status": "finished"},
            "policy_warnings": [],
            "created_at": datetime.utcnow() - timedelta(days=2),
        },
        {
            "doctor_id": doctor_id,
            "doctor_name": "Test Doctor",
            "patient_id": patient2_id,
            "patient_name": "P2",
            "raw_transcript": "Patient presents with severe epigastric pain for 1 week, worse after meals. History of alcohol use. Tenderness in epigastric region. Suspecting gastritis. Prescribing Pantoprazole 40mg and Domperidone 10mg. Ordering endoscopy.",
            "symptoms": ["severe epigastric pain", "pain worse after meals"],
            "diagnosis": "Chronic Gastritis",
            "prescriptions": [
                {"medication": "Pantoprazole 40mg", "dosage": "1 tablet", "frequency": "before breakfast", "duration": "14 days", "is_covered": True, "alternative": None},
                {"medication": "Domperidone 10mg", "dosage": "1 tablet", "frequency": "3 times daily before meals", "duration": "7 days", "is_covered": True, "alternative": None},
                {"medication": "Sucralfate Suspension", "dosage": "10ml", "frequency": "4 times daily", "duration": "14 days", "is_covered": False, "alternative": "Generic Sucralfate tablets"},
            ],
            "icd_codes": ["K29.7"],
            "notes": "Endoscopy recommended. Advised to avoid alcohol and spicy food.",
            "fhir_encounter": {"resourceType": "Encounter", "status": "finished"},
            "policy_warnings": ["Sucralfate Suspension is NOT covered. Switch to Generic Sucralfate tablets for claim approval."],
            "created_at": datetime.utcnow() - timedelta(days=1),
        },
    ]

    note_results = await db.clinical_notes.insert_many(notes)
    note_ids = [str(nid) for nid in note_results.inserted_ids]
    print(f"Created {len(notes)} clinical notes")

    # ── Claims ──
    claims = [
        {
            "doctor_id": doctor_id,
            "doctor_name": "Test Doctor",
            "patient_id": patient1_id,
            "patient_name": "P1",
            "policy_number": "STD-78901",
            "insurer_name": "Star Health Insurance",
            "clinical_note_id": note_ids[0],
            "diagnosis": "Acute Upper Respiratory Infection",
            "icd_codes": ["J06.9"],
            "items": [
                {"description": "Consultation Fee", "icd_code": "J06.9", "amount": 500, "category": "consultation"},
                {"description": "Paracetamol 500mg x 15", "icd_code": None, "amount": 45, "category": "medication"},
                {"description": "Azithromycin 500mg x 3", "icd_code": None, "amount": 120, "category": "medication"},
                {"description": "Cetirizine 10mg x 5", "icd_code": None, "amount": 25, "category": "medication"},
                {"description": "CBC Blood Test", "icd_code": None, "amount": 300, "category": "lab"},
            ],
            "total_amount": 990,
            "room_type": None,
            "status": "approved",
            "adjudication_notes": "Auto-approved: standard procedure with valid ICD codes",
            "rejection_reason": None,
            "flag_reasons": [],
            "approved_amount": 990,
            "submitted_at": datetime.utcnow() - timedelta(days=2),
            "adjudicated_at": datetime.utcnow() - timedelta(days=1),
        },
        {
            # NEGATIVE PATH DEMO — P2 submitted without coverage check
            # Sucralfate NOT substituted, private room exceeds STD cap
            "hospital_id": None,
            "hospital_name": "Test Hospital",
            "submitted_by": "hospital",
            "doctor_id": doctor_id,
            "doctor_name": "Test Doctor",
            "patient_id": patient2_id,
            "patient_name": "P2",
            "policy_number": "STD-45678",
            "insurer_name": "HDFC Ergo",
            "clinical_note_id": note_ids[1],
            "diagnosis": "Chronic Gastritis — Unverified Coverage",
            "icd_codes": ["K29.7"],
            "items": [
                {"description": "Doctor Consultation Fee", "icd_code": "K29.7", "amount": 600, "category": "consultation"},
                {"description": "Pantoprazole 40mg", "icd_code": None, "amount": 150, "category": "medication"},
                {"description": "Domperidone 10mg", "icd_code": None, "amount": 150, "category": "medication"},
                {"description": "Sucralfate Suspension", "icd_code": None, "amount": 150, "category": "medication"},
                {"description": "Room Charges (Private, 2 days)", "icd_code": None, "amount": 12000, "category": "room"},
                {"description": "Upper GI Endoscopy", "icd_code": "K29.7", "amount": 5000, "category": "procedure"},
            ],
            "total_amount": 18050,
            "room_type": "private",
            "status": "pending",
            "adjudication_notes": None,
            "rejection_reason": None,
            "flag_reasons": [],
            "approved_amount": None,
            "submitted_at": datetime.utcnow() - timedelta(days=1),
            "adjudicated_at": None,
        },
        {
            "doctor_id": doctor_id,
            "doctor_name": "Test Doctor",
            "patient_id": patient1_id,
            "patient_name": "P1",
            "policy_number": "STD-78901",
            "insurer_name": "Star Health Insurance",
            "clinical_note_id": note_ids[0],
            "diagnosis": "Follow-up: Respiratory Infection",
            "icd_codes": ["J06.9"],
            "items": [
                {"description": "Follow-up Consultation", "icd_code": "J06.9", "amount": 300, "category": "consultation"},
                {"description": "Chest X-Ray", "icd_code": None, "amount": 400, "category": "lab"},
            ],
            "total_amount": 700,
            "room_type": None,
            "status": "pending",
            "adjudication_notes": None,
            "rejection_reason": None,
            "flag_reasons": [],
            "approved_amount": None,
            "submitted_at": datetime.utcnow(),
            "adjudicated_at": None,
        },
        {
            # REJECTED PATH DEMO — P1 submits dental + vitamins (policy exclusions)
            "doctor_id": doctor_id,
            "doctor_name": "Test Doctor",
            "patient_id": patient1_id,
            "patient_name": "P1",
            "policy_number": "STD-78901",
            "insurer_name": "Star Health Insurance",
            "clinical_note_id": None,
            "diagnosis": "Dental Checkup and Nutritional Review",
            "icd_codes": ["K08.9"],
            "items": [
                {"description": "Dental Cleaning Procedure", "icd_code": "K08.9", "amount": 2500, "category": "procedure"},
                {"description": "Dental X-Ray", "icd_code": "K08.9", "amount": 800, "category": "lab"},
                {"description": "Vitamins and Supplements Pack", "icd_code": None, "amount": 600, "category": "medication"},
                {"description": "Consultation Fee", "icd_code": "K08.9", "amount": 500, "category": "consultation"},
            ],
            "total_amount": 4400,
            "room_type": None,
            "status": "pending",
            "adjudication_notes": None,
            "rejection_reason": None,
            "flag_reasons": [],
            "approved_amount": None,
            "submitted_at": datetime.utcnow() - timedelta(hours=3),
            "adjudicated_at": None,
        },
    ]

    await db.claims.insert_many(claims)
    print(f"Created {len(claims)} claims (1 approved, 1 flagged, 2 pending, 1 rejection-path)")

    # ── Health Checks ──
    health_checks = [
        {
            "patient_id": patient1_id,
            "patient_name": "P1",
            "doctor_id": doctor_id,
            "wound_condition": "normal",
            "fever": False,
            "temperature": 36.8,
            "pain_level": 2,
            "appetite": "normal",
            "mobility": "normal",
            "medication_taken": True,
            "additional_notes": "Feeling much better today.",
            "is_flagged": False,
            "flag_reasons": [],
            "doctor_notified": False,
            "created_at": datetime.utcnow() - timedelta(days=1),
        },
        {
            "patient_id": patient1_id,
            "patient_name": "P1",
            "doctor_id": doctor_id,
            "wound_condition": "red",
            "fever": True,
            "temperature": 38.7,
            "pain_level": 6,
            "appetite": "reduced",
            "mobility": "limited",
            "medication_taken": True,
            "additional_notes": "Wound area looks red and warm. Slight fever returned.",
            "is_flagged": True,
            "flag_reasons": [
                "Wound condition: red — possible infection",
                "Patient reports fever",
                "High temperature: 38.7°C",
                "Moderate pain level: 6/10"
            ],
            "doctor_notified": True,
            "created_at": datetime.utcnow(),
        },
    ]

    await db.health_checks.insert_many(health_checks)
    print(f"Created {len(health_checks)} health checks (1 normal, 1 flagged)")

    # Create indexes
    await db.users.create_index("email", unique=True)
    await db.claims.create_index("patient_id")
    await db.claims.create_index("doctor_id")
    await db.claims.create_index("status")
    await db.clinical_notes.create_index("doctor_id")
    await db.clinical_notes.create_index("patient_id")
    await db.health_checks.create_index("patient_id")

    print("\n✓ Seed data loaded successfully!")
    print("\nDemo accounts (password: password123):")
    print("  Doctor:  doctor@demo.com")
    print("  Insurer: insurer@demo.com")
    print("  Patient: patient@demo.com")

    client.close()


if __name__ == "__main__":
    asyncio.run(seed())
