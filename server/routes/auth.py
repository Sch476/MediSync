"""Authentication routes — register and login with JWT."""
from fastapi import APIRouter, HTTPException, status
from datetime import datetime

from database import get_db
from models.user import UserCreate, UserLogin, UserResponse
from middleware.auth_middleware import hash_password, verify_password, create_access_token

router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """Register a new user (doctor, insurer, or patient)."""
    db = get_db()

    # Check if email already exists
    existing = await db.users.find_one({"email": user_data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Build user document
    user_doc = {
        "email": user_data.email,
        "hashed_password": hash_password(user_data.password),
        "full_name": user_data.full_name,
        "role": user_data.role,
        "license_number": user_data.license_number,
        "specialization": user_data.specialization,
        "policy_number": user_data.policy_number,
        "insurer_name": user_data.insurer_name,
        "created_at": datetime.utcnow(),
    }

    result = await db.users.insert_one(user_doc)
    user_id = str(result.inserted_id)

    # Generate JWT token
    token = create_access_token(data={"sub": user_id, "role": user_data.role})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user_id,
            "email": user_data.email,
            "full_name": user_data.full_name,
            "role": user_data.role,
        },
    }


@router.post("/login")
async def login(credentials: UserLogin):
    """Login and receive a JWT token."""
    db = get_db()

    user = await db.users.find_one({"email": credentials.email})
    if not user or not verify_password(credentials.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    user_id = str(user["_id"])
    token = create_access_token(data={"sub": user_id, "role": user["role"]})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user_id,
            "email": user["email"],
            "full_name": user["full_name"],
            "role": user["role"],
            "license_number": user.get("license_number"),
            "specialization": user.get("specialization"),
            "policy_number": user.get("policy_number"),
            "insurer_name": user.get("insurer_name"),
        },
    }


@router.get("/me")
async def get_me(current_user: dict = None):
    """Get current user profile. Requires auth middleware at route level."""
    from fastapi import Depends
    from middleware.auth_middleware import get_current_user
    # This is re-registered below with proper dependency
    pass


# Proper /me endpoint with dependency injection
from fastapi import Depends
from middleware.auth_middleware import get_current_user


@router.get("/me/profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    """Get current authenticated user's profile."""
    return {
        "id": current_user["id"],
        "email": current_user["email"],
        "full_name": current_user["full_name"],
        "role": current_user["role"],
        "license_number": current_user.get("license_number"),
        "specialization": current_user.get("specialization"),
        "policy_number": current_user.get("policy_number"),
        "insurer_name": current_user.get("insurer_name"),
    }
