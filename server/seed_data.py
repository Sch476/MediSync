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

    for collection in ["users", "clinical_notes", "claims", "health_checks", "policy_documents", "bill_analyses", "daily_bills"]:
        await db[collection].drop()

    print("Cleared existing data.")

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

    hospital = {
        "email": "hospital@demo.com",
        "hashed_password": hashed_pw,
        "full_name": "Test Hospital",
        "role": "hospital",
        "license_number": None,
        "specialization": None,
        "policy_number": None,
        "insurer_name": None,
        "hospital_name": "Apollo Hospital, Bengaluru",
        "created_at": datetime.utcnow(),
    }

    users = await db.users.insert_many([doctor, insurer, patient1, patient2, hospital])
    doctor_id = str(users.inserted_ids[0])
    insurer_id = str(users.inserted_ids[1])
    patient1_id = str(users.inserted_ids[2])
    patient2_id = str(users.inserted_ids[3])
    hospital_id = str(users.inserted_ids[4])

    print(f"Created 5 users: doctor, insurer, 2 patients, hospital")

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


        {
            "doctor_id": doctor_id,
            "doctor_name": "Test Doctor",
            "hospital_name": "Apollo Hospital, Bengaluru",
            "patient_id": patient1_id,
            "patient_name": "P1",
            "policy_number": "STD-78901",
            "insurer_name": "Star Health Insurance",
            "clinical_note_id": None,
            "diagnosis": "Uncomplicated Urinary Tract Infection",
            "icd_codes": ["N39.0"],
            "items": [
                {"description": "Consultation Fee", "icd_code": "N39.0", "amount": 500, "category": "consultation"},
                {"description": "Urine Culture Test", "icd_code": None, "amount": 450, "category": "lab"},
                {"description": "Nitrofurantoin 100mg x 14", "icd_code": None, "amount": 220, "category": "medication"},
                {"description": "Paracetamol 500mg x 10", "icd_code": None, "amount": 40, "category": "medication"},
            ],
            "total_amount": 1210,
            "room_type": None,
            "status": "pending",
            "adjudication_notes": None, "rejection_reason": None, "flag_reasons": [], "approved_amount": None,
            "submitted_at": datetime.utcnow() - timedelta(days=12, hours=4),
            "adjudicated_at": None,
        },

        {
            "doctor_id": doctor_id,
            "doctor_name": "Test Doctor",
            "hospital_name": "Fortis Healthcare, Mumbai",
            "patient_id": patient2_id,
            "patient_name": "P2",
            "policy_number": "STD-45678",
            "insurer_name": "HDFC Ergo",
            "clinical_note_id": None,
            "diagnosis": "Type 2 Diabetes Mellitus — Routine Review",
            "icd_codes": ["E11.9"],
            "items": [
                {"description": "Endocrinologist Consultation", "icd_code": "E11.9", "amount": 800, "category": "consultation"},
                {"description": "HbA1c Test", "icd_code": None, "amount": 650, "category": "lab"},
                {"description": "Fasting Blood Sugar", "icd_code": None, "amount": 200, "category": "lab"},
                {"description": "Metformin 500mg x 60", "icd_code": None, "amount": 180, "category": "medication"},
            ],
            "total_amount": 1830,
            "room_type": None,
            "status": "pending",
            "adjudication_notes": None, "rejection_reason": None, "flag_reasons": [], "approved_amount": None,
            "submitted_at": datetime.utcnow() - timedelta(days=10, hours=9),
            "adjudicated_at": None,
        },

        {
            "doctor_id": doctor_id,
            "doctor_name": "Test Doctor",
            "hospital_name": "Max Healthcare, Delhi",
            "patient_id": patient1_id,
            "patient_name": "P1",
            "policy_number": "STD-78901",
            "insurer_name": "Star Health Insurance",
            "clinical_note_id": None,
            "diagnosis": "Essential Hypertension — Medication Review",
            "icd_codes": ["I10"],
            "items": [
                {"description": "Cardiology Consultation", "icd_code": "I10", "amount": 700, "category": "consultation"},
                {"description": "ECG", "icd_code": None, "amount": 350, "category": "lab"},
                {"description": "Telmisartan 40mg x 30", "icd_code": None, "amount": 220, "category": "medication"},
                {"description": "Amlodipine 5mg x 30", "icd_code": None, "amount": 95, "category": "medication"},
            ],
            "total_amount": 1365,
            "room_type": None,
            "status": "pending",
            "adjudication_notes": None, "rejection_reason": None, "flag_reasons": [], "approved_amount": None,
            "submitted_at": datetime.utcnow() - timedelta(days=9, hours=2),
            "adjudicated_at": None,
        },

        {
            "doctor_id": doctor_id,
            "doctor_name": "Test Doctor",
            "hospital_name": "Dermacare Skin Clinic, Pune",
            "patient_id": patient2_id,
            "patient_name": "P2",
            "policy_number": "STD-45678",
            "insurer_name": "HDFC Ergo",
            "clinical_note_id": None,
            "diagnosis": "Skin Cosmetic Consultation",
            "icd_codes": ["L98.9"],
            "items": [
                {"description": "Cosmetic Skin Peel Procedure", "icd_code": None, "amount": 6500, "category": "procedure"},
                {"description": "Cosmetic Laser Touch-up", "icd_code": None, "amount": 4500, "category": "procedure"},
                {"description": "Dermatology Consultation", "icd_code": "L98.9", "amount": 1000, "category": "consultation"},
            ],
            "total_amount": 12000,
            "room_type": None,
            "status": "pending",
            "adjudication_notes": None, "rejection_reason": None, "flag_reasons": [], "approved_amount": None,
            "submitted_at": datetime.utcnow() - timedelta(days=8, hours=6),
            "adjudicated_at": None,
        },

        {
            "doctor_id": doctor_id,
            "doctor_name": "Test Doctor",
            "hospital_name": "Nova IVF Fertility, Hyderabad",
            "patient_id": patient1_id,
            "patient_name": "P1",
            "policy_number": "STD-78901",
            "insurer_name": "Star Health Insurance",
            "clinical_note_id": None,
            "diagnosis": "Fertility Treatment Consultation",
            "icd_codes": ["N97.9"],
            "items": [
                {"description": "IVF Cycle — First Round", "icd_code": None, "amount": 125000, "category": "procedure"},
                {"description": "Fertility Hormone Panel", "icd_code": None, "amount": 4500, "category": "lab"},
                {"description": "Fertility Specialist Consultation", "icd_code": "N97.9", "amount": 1500, "category": "consultation"},
            ],
            "total_amount": 131000,
            "room_type": None,
            "status": "pending",
            "adjudication_notes": None, "rejection_reason": None, "flag_reasons": [], "approved_amount": None,
            "submitted_at": datetime.utcnow() - timedelta(days=7, hours=1),
            "adjudicated_at": None,
        },

        {
            "doctor_id": doctor_id,
            "doctor_name": "Test Doctor",
            "hospital_name": "Tata Memorial Centre, Mumbai",
            "patient_id": patient2_id,
            "patient_name": "P2",
            "policy_number": "STD-45678",
            "insurer_name": "HDFC Ergo",
            "clinical_note_id": None,
            "diagnosis": "Breast Cancer — Chemotherapy Cycle 3 of 6",
            "icd_codes": ["C50.9", "Z51.11"],
            "items": [
                {"description": "Oncologist Consultation", "icd_code": "C50.9", "amount": 1500, "category": "consultation"},
                {"description": "Chemotherapy Drug Protocol (AC)", "icd_code": "Z51.11", "amount": 45000, "category": "medication"},
                {"description": "Day-care IV Infusion Charges", "icd_code": None, "amount": 8000, "category": "procedure"},
                {"description": "CBC + LFT Monitoring Panel", "icd_code": None, "amount": 1200, "category": "lab"},
                {"description": "Anti-emetic Injection (Ondansetron)", "icd_code": None, "amount": 600, "category": "medication"},
            ],
            "total_amount": 56300,
            "room_type": None,
            "status": "pending",
            "adjudication_notes": None, "rejection_reason": None, "flag_reasons": [], "approved_amount": None,
            "submitted_at": datetime.utcnow() - timedelta(days=6, hours=10),
            "adjudicated_at": None,
        },

        {
            "doctor_id": doctor_id,
            "doctor_name": "Test Doctor",
            "hospital_name": "AIIMS, New Delhi",
            "patient_id": patient1_id,
            "patient_name": "P1",
            "policy_number": "STD-78901",
            "insurer_name": "Star Health Insurance",
            "clinical_note_id": None,
            "diagnosis": "Acute Myocardial Infarction — Angioplasty Performed",
            "icd_codes": ["I21.9"],
            "items": [
                {"description": "Emergency Admission Charges", "icd_code": None, "amount": 5000, "category": "consultation"},
                {"description": "Coronary Angioplasty with Stent", "icd_code": "I21.9", "amount": 185000, "category": "procedure"},
                {"description": "ICU Room (2 days)", "icd_code": None, "amount": 28000, "category": "room"},
                {"description": "Cardiac Enzymes + Troponin-I", "icd_code": None, "amount": 3200, "category": "lab"},
                {"description": "Post-op Medications", "icd_code": None, "amount": 2400, "category": "medication"},
            ],
            "total_amount": 223600,
            "room_type": "icu",
            "status": "pending",
            "adjudication_notes": None, "rejection_reason": None, "flag_reasons": [], "approved_amount": None,
            "submitted_at": datetime.utcnow() - timedelta(days=5, hours=22),
            "adjudicated_at": None,
        },

        {
            "doctor_id": doctor_id,
            "doctor_name": "Test Doctor",
            "hospital_name": "Manipal Hospitals, Bengaluru",
            "patient_id": patient2_id,
            "patient_name": "P2",
            "policy_number": "STD-45678",
            "insurer_name": "HDFC Ergo",
            "clinical_note_id": None,
            "diagnosis": "Acute Appendicitis — Laparoscopic Surgery",
            "icd_codes": ["K35.80"],
            "items": [
                {"description": "Surgeon Consultation", "icd_code": "K35.80", "amount": 1500, "category": "consultation"},
                {"description": "Laparoscopic Appendectomy", "icd_code": "K35.80", "amount": 48000, "category": "procedure"},
                {"description": "OT Charges + Anaesthesia", "icd_code": None, "amount": 12000, "category": "procedure"},
                {"description": "Semi-private Room (2 days)", "icd_code": None, "amount": 6000, "category": "room"},
                {"description": "Post-op Antibiotics", "icd_code": None, "amount": 1800, "category": "medication"},
            ],
            "total_amount": 69300,
            "room_type": "semi-private",
            "status": "pending",
            "adjudication_notes": None, "rejection_reason": None, "flag_reasons": [], "approved_amount": None,
            "submitted_at": datetime.utcnow() - timedelta(days=4, hours=14),
            "adjudicated_at": None,
        },

        {
            "doctor_id": doctor_id,
            "doctor_name": "Test Doctor",
            "hospital_name": "Kokilaben Hospital, Mumbai",
            "patient_id": patient2_id,
            "patient_name": "P2",
            "policy_number": "STD-45678",
            "insurer_name": "HDFC Ergo",
            "clinical_note_id": None,
            "diagnosis": "Pneumonia — Inpatient Care",
            "icd_codes": ["J18.9"],
            "items": [
                {"description": "Pulmonology Consultation", "icd_code": "J18.9", "amount": 1200, "category": "consultation"},
                {"description": "Private Room (3 days @ ₹7500/day)", "icd_code": None, "amount": 22500, "category": "room"},
                {"description": "Chest X-Ray + Sputum Culture", "icd_code": None, "amount": 2100, "category": "lab"},
                {"description": "IV Antibiotics Course", "icd_code": None, "amount": 4800, "category": "medication"},
                {"description": "Nebulisation Charges", "icd_code": None, "amount": 900, "category": "procedure"},
            ],
            "total_amount": 31500,
            "room_type": "private",
            "status": "pending",
            "adjudication_notes": None, "rejection_reason": None, "flag_reasons": [], "approved_amount": None,
            "submitted_at": datetime.utcnow() - timedelta(days=3, hours=7),
            "adjudicated_at": None,
        },

        {
            "doctor_id": doctor_id,
            "doctor_name": "Test Doctor",
            "hospital_name": "Sankara Eye Hospital, Chennai",
            "patient_id": patient1_id,
            "patient_name": "P1",
            "policy_number": "STD-78901",
            "insurer_name": "Star Health Insurance",
            "clinical_note_id": None,
            "diagnosis": "Myopia — Refraction Check",
            "icd_codes": ["H52.1"],
            "items": [
                {"description": "Ophthalmologist Consultation", "icd_code": "H52.1", "amount": 500, "category": "consultation"},
                {"description": "Refraction Test", "icd_code": None, "amount": 300, "category": "lab"},
                {"description": "Spectacles (Frame + Lenses)", "icd_code": None, "amount": 4500, "category": "other"},
            ],
            "total_amount": 5300,
            "room_type": None,
            "status": "pending",
            "adjudication_notes": None, "rejection_reason": None, "flag_reasons": [], "approved_amount": None,
            "submitted_at": datetime.utcnow() - timedelta(days=2, hours=3),
            "adjudicated_at": None,
        },

        {
            "doctor_id": doctor_id,
            "doctor_name": "Test Doctor",
            "hospital_name": "Breach Candy Hospital, Mumbai",
            "patient_id": patient2_id,
            "patient_name": "P2",
            "policy_number": "STD-45678",
            "insurer_name": "HDFC Ergo",
            "clinical_note_id": None,
            "diagnosis": "Acute Asthma Exacerbation",
            "icd_codes": ["J45.9"],
            "items": [
                {"description": "Emergency Consultation", "icd_code": "J45.9", "amount": 800, "category": "consultation"},
                {"description": "Nebulisation (3 rounds)", "icd_code": None, "amount": 1200, "category": "procedure"},
                {"description": "Salbutamol Inhaler", "icd_code": None, "amount": 320, "category": "medication"},
                {"description": "Oral Prednisolone Course", "icd_code": None, "amount": 180, "category": "medication"},
                {"description": "Pulse Oximetry Monitoring", "icd_code": None, "amount": 400, "category": "procedure"},
            ],
            "total_amount": 2900,
            "room_type": None,
            "status": "pending",
            "adjudication_notes": None, "rejection_reason": None, "flag_reasons": [], "approved_amount": None,
            "submitted_at": datetime.utcnow() - timedelta(days=1, hours=8),
            "adjudicated_at": None,
        },

        {
            "doctor_id": doctor_id,
            "doctor_name": "Test Doctor",
            "hospital_name": "PD Hinduja Hospital, Mumbai",
            "patient_id": patient1_id,
            "patient_name": "P1",
            "policy_number": "STD-78901",
            "insurer_name": "Star Health Insurance",
            "clinical_note_id": None,
            "diagnosis": "Chronic Low Back Pain — Physiotherapy",
            "icd_codes": ["M54.5"],
            "items": [
                {"description": "Orthopedic Consultation", "icd_code": "M54.5", "amount": 700, "category": "consultation"},
                {"description": "Lumbar MRI", "icd_code": None, "amount": 6500, "category": "lab"},
                {"description": "Physiotherapy Sessions (5)", "icd_code": None, "amount": 2500, "category": "procedure"},
                {"description": "Diclofenac + Thiocolchicoside", "icd_code": None, "amount": 340, "category": "medication"},
            ],
            "total_amount": 10040,
            "room_type": None,
            "status": "pending",
            "adjudication_notes": None, "rejection_reason": None, "flag_reasons": [], "approved_amount": None,
            "submitted_at": datetime.utcnow() - timedelta(hours=18),
            "adjudicated_at": None,
        },

        {
            "doctor_id": doctor_id,
            "doctor_name": "Test Doctor",
            "hospital_name": "Columbia Asia Hospital, Bengaluru",
            "patient_id": patient2_id,
            "patient_name": "P2",
            "policy_number": "STD-45678",
            "insurer_name": "HDFC Ergo",
            "clinical_note_id": None,
            "diagnosis": "Acute Gastroenteritis with Dehydration",
            "icd_codes": ["A09"],
            "items": [
                {"description": "Emergency Consultation", "icd_code": "A09", "amount": 600, "category": "consultation"},
                {"description": "IV Fluids (Normal Saline + RL)", "icd_code": None, "amount": 900, "category": "procedure"},
                {"description": "Stool Culture + CBC", "icd_code": None, "amount": 850, "category": "lab"},
                {"description": "Ondansetron + ORS", "icd_code": None, "amount": 260, "category": "medication"},
                {"description": "Day-care Bed Charges", "icd_code": None, "amount": 1200, "category": "room"},
            ],
            "total_amount": 3810,
            "room_type": "general",
            "status": "pending",
            "adjudication_notes": None, "rejection_reason": None, "flag_reasons": [], "approved_amount": None,
            "submitted_at": datetime.utcnow() - timedelta(hours=5),
            "adjudicated_at": None,
        },

        {
            "doctor_id": doctor_id,
            "doctor_name": "Test Doctor",
            "hospital_name": "Tata Memorial Hospital, Mumbai",
            "patient_id": patient1_id,
            "patient_name": "P1",
            "policy_number": "STD-78901",
            "insurer_name": "Star Health Insurance",
            "clinical_note_id": None,
            "diagnosis": "Stage II Invasive Ductal Carcinoma of Breast",
            "icd_codes": ["C50.9"],
            "items": [
                {"description": "Oncologist Consultation", "icd_code": "C50.9", "amount": 2000, "category": "consultation"},
                {"description": "Mammography + Biopsy", "icd_code": "C50.9", "amount": 8500, "category": "lab"},
                {"description": "Tamoxifen 20mg x 30", "icd_code": None, "amount": 1200, "category": "medication"},
                {"description": "Pre-operative Workup", "icd_code": None, "amount": 4500, "category": "procedure"},
            ],
            "total_amount": 16200,
            "room_type": None,
            "status": "pending",
            "adjudication_notes": None, "rejection_reason": None, "flag_reasons": [], "approved_amount": None,
            "submitted_at": datetime.utcnow() - timedelta(hours=8),
            "adjudicated_at": None,
        },

        {
            "doctor_id": doctor_id,
            "doctor_name": "Test Doctor",
            "hospital_name": "Fortis Hospital, Bengaluru",
            "patient_id": patient2_id,
            "patient_name": "P2",
            "policy_number": "STD-45678",
            "insurer_name": "HDFC Ergo",
            "clinical_note_id": None,
            "diagnosis": "Acute Myocardial Infarction — Coronary Bypass Performed",
            "icd_codes": ["I21.4"],
            "items": [
                {"description": "Emergency Cardiac Consultation", "icd_code": "I21.4", "amount": 3000, "category": "consultation"},
                {"description": "Coronary Angiography", "icd_code": "I21.4", "amount": 25000, "category": "procedure"},
                {"description": "CABG (Coronary Artery Bypass Graft)", "icd_code": "I21.4", "amount": 180000, "category": "procedure"},
                {"description": "ICU Stay (4 days)", "icd_code": None, "amount": 48000, "category": "room"},
                {"description": "Post-op Medications", "icd_code": None, "amount": 6500, "category": "medication"},
            ],
            "total_amount": 262500,
            "room_type": "icu",
            "status": "pending",
            "adjudication_notes": None, "rejection_reason": None, "flag_reasons": [], "approved_amount": None,
            "submitted_at": datetime.utcnow() - timedelta(hours=12),
            "adjudicated_at": None,
        },

        {
            "doctor_id": doctor_id,
            "doctor_name": "Test Doctor",
            "hospital_name": "Manipal Hospital, Bengaluru",
            "patient_id": patient1_id,
            "patient_name": "P1",
            "policy_number": "STD-78901",
            "insurer_name": "Star Health Insurance",
            "clinical_note_id": None,
            "diagnosis": "Right Total Knee Joint Replacement Surgery",
            "icd_codes": ["M17.11"],
            "items": [
                {"description": "Orthopedic Surgeon Consultation", "icd_code": "M17.11", "amount": 1500, "category": "consultation"},
                {"description": "Pre-operative Workup + MRI", "icd_code": None, "amount": 8500, "category": "lab"},
                {"description": "Total Knee Replacement Surgery", "icd_code": "M17.11", "amount": 320000, "category": "procedure"},
                {"description": "Implant (Cobalt-Chrome Prosthesis)", "icd_code": None, "amount": 120000, "category": "procedure"},
                {"description": "Private Room (7 days)", "icd_code": None, "amount": 56000, "category": "room"},
                {"description": "Physiotherapy Sessions", "icd_code": None, "amount": 4500, "category": "procedure"},
            ],
            "total_amount": 510500,
            "room_type": "private",
            "status": "pending",
            "adjudication_notes": None, "rejection_reason": None, "flag_reasons": [], "approved_amount": None,
            "submitted_at": datetime.utcnow() - timedelta(hours=20),
            "adjudicated_at": None,
        },

        {
            "doctor_id": doctor_id,
            "doctor_name": "Test Doctor",
            "hospital_name": "HCG Cancer Centre, Bengaluru",
            "patient_id": patient2_id,
            "patient_name": "P2",
            "policy_number": "STD-45678",
            "insurer_name": "HDFC Ergo",
            "clinical_note_id": None,
            "diagnosis": "Chemotherapy Session 3 of 6 — Non-Hodgkin Lymphoma",
            "icd_codes": ["Z51.11", "C85.9"],
            "items": [
                {"description": "Oncology Consultation", "icd_code": "Z51.11", "amount": 2500, "category": "consultation"},
                {"description": "Chemotherapy Drug Infusion (R-CHOP)", "icd_code": "Z51.11", "amount": 85000, "category": "medication"},
                {"description": "Day-care Bed Charges", "icd_code": None, "amount": 4500, "category": "room"},
                {"description": "Antiemetics + Pre-medication", "icd_code": None, "amount": 1800, "category": "medication"},
                {"description": "CBC + LFT + Renal Panel", "icd_code": None, "amount": 1200, "category": "lab"},
            ],
            "total_amount": 95000,
            "room_type": "general",
            "status": "pending",
            "adjudication_notes": None, "rejection_reason": None, "flag_reasons": [], "approved_amount": None,
            "submitted_at": datetime.utcnow() - timedelta(hours=2),
            "adjudicated_at": None,
        },

        {
            "doctor_id": doctor_id,
            "doctor_name": "Test Doctor",
            "hospital_name": "Apollo Hospital, Bengaluru",
            "patient_id": patient1_id,
            "patient_name": "P1",
            "policy_number": "STD-78901",
            "insurer_name": "Star Health Insurance",
            "clinical_note_id": None,
            "diagnosis": "Type 2 Diabetes Mellitus — Quarterly Follow-up",
            "icd_codes": ["E11.9"],
            "items": [
                {"description": "Endocrinologist Consultation", "icd_code": "E11.9", "amount": 800, "category": "consultation"},
                {"description": "HbA1c Test", "icd_code": None, "amount": 600, "category": "lab"},
                {"description": "Lipid Profile", "icd_code": None, "amount": 700, "category": "lab"},
                {"description": "Metformin 500mg x 60", "icd_code": None, "amount": 240, "category": "medication"},
                {"description": "Glimepiride 2mg x 30", "icd_code": None, "amount": 180, "category": "medication"},
            ],
            "total_amount": 2520,
            "room_type": None,
            "status": "approved",
            "adjudication_notes": "Auto-approved: routine diabetic follow-up within policy limits",
            "rejection_reason": None,
            "flag_reasons": [],
            "approved_amount": 2520,
            "submitted_at": datetime.utcnow() - timedelta(days=14),
            "adjudicated_at": datetime.utcnow() - timedelta(days=13),
        },

        {
            "doctor_id": doctor_id,
            "doctor_name": "Test Doctor",
            "hospital_name": "Apollo Hospital, Bengaluru",
            "patient_id": patient1_id,
            "patient_name": "P1",
            "policy_number": "STD-78901",
            "insurer_name": "Star Health Insurance",
            "clinical_note_id": None,
            "diagnosis": "Hypertension Medication Review",
            "icd_codes": ["I10"],
            "items": [
                {"description": "Cardiologist Consultation", "icd_code": "I10", "amount": 1000, "category": "consultation"},
                {"description": "ECG", "icd_code": "I10", "amount": 400, "category": "lab"},
                {"description": "2D Echo", "icd_code": "I10", "amount": 2500, "category": "lab"},
                {"description": "Amlodipine 5mg x 30", "icd_code": None, "amount": 150, "category": "medication"},
                {"description": "Private Room (1 day)", "icd_code": None, "amount": 6000, "category": "room"},
            ],
            "total_amount": 10050,
            "room_type": "private",
            "status": "approved",
            "adjudication_notes": "Approved with adjustment — room rent ₹6000 reduced to standard cap ₹4000",
            "rejection_reason": None,
            "flag_reasons": ["Room rent ₹6000/day exceeds cap ₹4000/day. Excess: ₹2000"],
            "approved_amount": 8050,
            "submitted_at": datetime.utcnow() - timedelta(days=7),
            "adjudicated_at": datetime.utcnow() - timedelta(days=6),
        },

        {
            "doctor_id": doctor_id,
            "doctor_name": "Test Doctor",
            "hospital_name": "Apollo Hospital, Bengaluru",
            "patient_id": patient1_id,
            "patient_name": "P1",
            "policy_number": "STD-78901",
            "insurer_name": "Star Health Insurance",
            "clinical_note_id": None,
            "diagnosis": "Skin Cosmetic Consultation",
            "icd_codes": ["L70.0"],
            "items": [
                {"description": "Dermatologist Consultation", "icd_code": "L70.0", "amount": 800, "category": "consultation"},
                {"description": "Chemical Peel - Cosmetic", "icd_code": None, "amount": 4500, "category": "procedure"},
                {"description": "Skin Brightening Cream", "icd_code": None, "amount": 1200, "category": "medication"},
            ],
            "total_amount": 6500,
            "room_type": None,
            "status": "rejected",
            "adjudication_notes": "Rejected by insurer: Cosmetic procedures excluded under standard policy",
            "rejection_reason": "Cosmetic procedures excluded under standard policy",
            "flag_reasons": [],
            "approved_amount": 0,
            "submitted_at": datetime.utcnow() - timedelta(days=21),
            "adjudicated_at": datetime.utcnow() - timedelta(days=20),
        },
    ]

    await db.claims.insert_many(claims)
    print(f"Created {len(claims)} claims (mix of approved/flagged/pending for adjudication demo)")

    daily_bills = [
        {
            "hospital_id": hospital_id,
            "hospital_name": "Apollo Hospital, Bengaluru",
            "patient_id": patient1_id,
            "patient_name": "P1",
            "policy_number": "STD-78901",
            "insurer_name": "Star Health Insurance",
            "bill_date": (datetime.utcnow() - timedelta(days=3)).date().isoformat(),
            "items": [
                {"description": "Doctor Consultation Fee", "category": "consultation", "amount": 600, "is_covered": True, "coverage_reason": "Standard consultation — covered under OPD benefit"},
                {"description": "Paracetamol 650mg", "category": "medication", "amount": 150, "is_covered": True, "coverage_reason": "Listed in covered formulary (Section 3.2)"},
                {"description": "Multivitamin Supplements", "category": "medication", "amount": 450, "is_covered": False, "coverage_reason": "Excluded — vitamins and supplements (Section 3.3)"},
                {"description": "Cosmetic Skin Cream", "category": "medication", "amount": 800, "is_covered": False, "coverage_reason": "Excluded — cosmetic items (Section 3.3)"},
            ],
            "insurer_items": [
                {"description": "Doctor Consultation Fee", "category": "consultation", "amount": 600, "is_covered": True, "coverage_reason": "Standard consultation — covered under OPD benefit"},
                {"description": "Paracetamol 650mg", "category": "medication", "amount": 150, "is_covered": True, "coverage_reason": "Listed in covered formulary (Section 3.2)"},
            ],
            "patient_items": [
                {"description": "Multivitamin Supplements", "category": "medication", "amount": 450, "is_covered": False, "coverage_reason": "Excluded — vitamins and supplements (Section 3.3)"},
                {"description": "Cosmetic Skin Cream", "category": "medication", "amount": 800, "is_covered": False, "coverage_reason": "Excluded — cosmetic items (Section 3.3)"},
            ],
            "insurer_total": 750,
            "patient_total": 1250,
            "total_amount": 2000,
            "status": "submitted",
            "claim_id": None,
            "created_at": datetime.utcnow() - timedelta(days=3),
            "submitted_at": datetime.utcnow() - timedelta(days=3),
            "patient_paid": False,
        },

        {
            "hospital_id": hospital_id,
            "hospital_name": "Apollo Hospital, Bengaluru",
            "patient_id": patient1_id,
            "patient_name": "P1",
            "policy_number": "STD-78901",
            "insurer_name": "Star Health Insurance",
            "bill_date": (datetime.utcnow() - timedelta(days=1)).date().isoformat(),
            "items": [
                {"description": "Room Charges (Private, 1 day)", "category": "room", "amount": 6000, "is_covered": True, "coverage_reason": "Standard room rent within cap"},
                {"description": "Nursing Care", "category": "other", "amount": 500, "is_covered": True, "coverage_reason": "Included in inpatient benefit"},
                {"description": "Dental Cleaning - Routine", "category": "procedure", "amount": 1500, "is_covered": False, "coverage_reason": "Excluded — dental procedures (Section 3.3)"},
                {"description": "Hearing Aid Battery", "category": "other", "amount": 350, "is_covered": False, "coverage_reason": "Excluded — hearing aids and accessories (Section 3.3)"},
            ],
            "insurer_items": [
                {"description": "Room Charges (Private, 1 day)", "category": "room", "amount": 6000, "is_covered": True, "coverage_reason": "Standard room rent within cap"},
                {"description": "Nursing Care", "category": "other", "amount": 500, "is_covered": True, "coverage_reason": "Included in inpatient benefit"},
            ],
            "patient_items": [
                {"description": "Dental Cleaning - Routine", "category": "procedure", "amount": 1500, "is_covered": False, "coverage_reason": "Excluded — dental procedures (Section 3.3)"},
                {"description": "Hearing Aid Battery", "category": "other", "amount": 350, "is_covered": False, "coverage_reason": "Excluded — hearing aids and accessories (Section 3.3)"},
            ],
            "insurer_total": 6500,
            "patient_total": 1850,
            "total_amount": 8350,
            "status": "submitted",
            "claim_id": None,
            "created_at": datetime.utcnow() - timedelta(days=1),
            "submitted_at": datetime.utcnow() - timedelta(days=1),
            "patient_paid": False,
        },

        {
            "hospital_id": hospital_id,
            "hospital_name": "Apollo Hospital, Bengaluru",
            "patient_id": patient1_id,
            "patient_name": "P1",
            "policy_number": "STD-78901",
            "insurer_name": "Star Health Insurance",
            "bill_date": (datetime.utcnow() - timedelta(days=10)).date().isoformat(),
            "items": [
                {"description": "ECG", "category": "lab", "amount": 400, "is_covered": True, "coverage_reason": "Diagnostic test — covered"},
                {"description": "Ayurvedic Supplement Pack", "category": "medication", "amount": 950, "is_covered": False, "coverage_reason": "Excluded — supplements (Section 3.3)"},
            ],
            "insurer_items": [
                {"description": "ECG", "category": "lab", "amount": 400, "is_covered": True, "coverage_reason": "Diagnostic test — covered"},
            ],
            "patient_items": [
                {"description": "Ayurvedic Supplement Pack", "category": "medication", "amount": 950, "is_covered": False, "coverage_reason": "Excluded — supplements (Section 3.3)"},
            ],
            "insurer_total": 400,
            "patient_total": 950,
            "total_amount": 1350,
            "status": "submitted",
            "claim_id": None,
            "created_at": datetime.utcnow() - timedelta(days=10),
            "submitted_at": datetime.utcnow() - timedelta(days=10),
            "patient_paid": True,
            "patient_paid_at": datetime.utcnow() - timedelta(days=9),
        },
    ]

    await db.daily_bills.insert_many(daily_bills)
    unpaid = sum(1 for b in daily_bills if not b.get("patient_paid"))
    print(f"Created {len(daily_bills)} daily bills ({unpaid} unpaid for Payable demo)")

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

    await db.users.create_index("email", unique=True)
    await db.claims.create_index("patient_id")
    await db.claims.create_index("doctor_id")
    await db.claims.create_index("status")
    await db.clinical_notes.create_index("doctor_id")
    await db.clinical_notes.create_index("patient_id")
    await db.health_checks.create_index("patient_id")

    print("\n✓ Seed data loaded successfully!")
    print("\nDemo accounts (password: password123):")
    print("  Doctor:   doctor@demo.com")
    print("  Insurer:  insurer@demo.com")
    print("  Patient:  patient@demo.com")
    print("  Hospital: hospital@demo.com")

    client.close()


if __name__ == "__main__":
    asyncio.run(seed())
