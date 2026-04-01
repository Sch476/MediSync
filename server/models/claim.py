"""Claim model — insurance claim submitted from doctor to insurer."""
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime


class ClaimItem(BaseModel):
    """Individual line item in a claim."""
    description: str
    icd_code: Optional[str] = None  # ICD-10 code
    amount: float
    category: str  # consultation, medication, procedure, room, lab


class ClaimCreate(BaseModel):
    patient_id: str
    patient_name: str
    policy_number: str
    insurer_name: str
    clinical_note_id: str
    diagnosis: str
    icd_codes: List[str] = []
    items: List[ClaimItem] = []
    total_amount: float
    room_type: Optional[str] = None  # general, semi-private, private, icu


class ClaimInDB(BaseModel):
    """Full claim document as stored in MongoDB."""
    doctor_id: str
    doctor_name: str
    patient_id: str
    patient_name: str
    policy_number: str
    insurer_name: str
    clinical_note_id: str
    diagnosis: str
    icd_codes: List[str] = []
    items: List[ClaimItem] = []
    total_amount: float
    room_type: Optional[str] = None
    # Adjudication fields
    status: Literal["pending", "approved", "rejected", "flagged"] = "pending"
    adjudication_notes: Optional[str] = None
    rejection_reason: Optional[str] = None
    flag_reasons: List[str] = []
    approved_amount: Optional[float] = None
    # Timestamps
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    adjudicated_at: Optional[datetime] = None


class ClaimResponse(BaseModel):
    id: str
    doctor_id: str
    doctor_name: str
    patient_id: str
    patient_name: str
    policy_number: str
    insurer_name: str
    diagnosis: str
    icd_codes: List[str]
    items: List[ClaimItem]
    total_amount: float
    room_type: Optional[str]
    status: str
    adjudication_notes: Optional[str]
    rejection_reason: Optional[str]
    flag_reasons: List[str]
    approved_amount: Optional[float]
    submitted_at: datetime
    adjudicated_at: Optional[datetime]
