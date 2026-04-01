"""Clinical note model — structured FHIR-compliant encounter from Smart Scribe."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class Prescription(BaseModel):
    medication: str
    dosage: str
    frequency: str
    duration: str
    is_covered: Optional[bool] = None  # RAG policy check result
    alternative: Optional[str] = None  # suggested generic if not covered


class ClinicalNoteCreate(BaseModel):
    patient_id: str
    patient_name: str
    raw_transcript: str  # Original speech-to-text transcript
    symptoms: List[str] = []
    diagnosis: str = ""
    prescriptions: List[Prescription] = []
    icd_codes: List[str] = []
    notes: Optional[str] = None


class ClinicalNoteInDB(BaseModel):
    """Full clinical note as stored in MongoDB."""
    doctor_id: str
    doctor_name: str
    patient_id: str
    patient_name: str
    raw_transcript: str
    symptoms: List[str]
    diagnosis: str
    prescriptions: List[Prescription]
    icd_codes: List[str]
    notes: Optional[str] = None
    # FHIR-compliant structured JSON
    fhir_encounter: Optional[dict] = None
    # Policy coverage check results
    policy_warnings: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ClinicalNoteResponse(BaseModel):
    id: str
    doctor_id: str
    doctor_name: str
    patient_id: str
    patient_name: str
    raw_transcript: str
    symptoms: List[str]
    diagnosis: str
    prescriptions: List[Prescription]
    icd_codes: List[str]
    notes: Optional[str]
    fhir_encounter: Optional[dict]
    policy_warnings: List[str]
    created_at: datetime
