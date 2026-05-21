"""Health check model — post-discharge daily check-in from patient."""
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


class HealthCheckCreate(BaseModel):
    wound_condition: Literal["normal", "red", "swollen", "discharge", "bleeding"]
    fever: bool = False
    temperature: Optional[float] = None
    pain_level: int = Field(..., ge=0, le=10)
    appetite: Literal["normal", "reduced", "none"]
    mobility: Literal["normal", "limited", "bedridden"]
    medication_taken: bool = True
    additional_notes: Optional[str] = None


class HealthCheckInDB(BaseModel):
    """Full health check document as stored in MongoDB."""
    patient_id: str
    patient_name: str
    doctor_id: str
    wound_condition: str
    fever: bool
    temperature: Optional[float]
    pain_level: int
    appetite: str
    mobility: str
    medication_taken: bool
    additional_notes: Optional[str]
    is_flagged: bool = False
    flag_reasons: list = []
    doctor_notified: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)


class HealthCheckResponse(BaseModel):
    id: str
    patient_id: str
    patient_name: str
    doctor_id: str
    wound_condition: str
    fever: bool
    temperature: Optional[float]
    pain_level: int
    appetite: str
    mobility: str
    medication_taken: bool
    additional_notes: Optional[str]
    is_flagged: bool
    flag_reasons: list
    doctor_notified: bool
    created_at: datetime
