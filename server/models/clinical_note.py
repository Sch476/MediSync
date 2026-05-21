"""Clinical note model — structured FHIR-compliant encounter from Smart Scribe."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class Prescription(BaseModel):
    medication: str
    dosage: str
    frequency: str = ""
    duration: str = ""
    is_new: Optional[bool] = None
    stopped: Optional[bool] = None
    is_covered: Optional[bool] = None
    alternative: Optional[str] = None


class ClinicalNoteCreate(BaseModel):
    patient_id: str
    patient_name: str
    raw_transcript: str
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
    fhir_encounter: Optional[dict] = None
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
