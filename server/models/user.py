"""User model — supports Doctor, Insurer (TPA), and Patient roles."""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str
    role: Literal["doctor", "insurer", "patient", "hospital"]
    # Doctor-specific
    license_number: Optional[str] = None
    specialization: Optional[str] = None
    # Patient-specific
    policy_number: Optional[str] = None
    insurer_name: Optional[str] = None
    # Hospital-specific
    hospital_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    license_number: Optional[str] = None
    specialization: Optional[str] = None
    policy_number: Optional[str] = None
    insurer_name: Optional[str] = None
    hospital_name: Optional[str] = None
    created_at: datetime


class UserInDB(BaseModel):
    """Full user document as stored in MongoDB."""
    email: str
    hashed_password: str
    full_name: str
    role: str
    license_number: Optional[str] = None
    specialization: Optional[str] = None
    policy_number: Optional[str] = None
    insurer_name: Optional[str] = None
    hospital_name: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
