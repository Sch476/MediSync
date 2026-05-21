"""MediSync FastAPI Application — Healthcare Middleware Platform."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from config import settings
from database import connect_db, close_db
from routes import auth, doctor, insurer, patient, hospital


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    await connect_db()
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("audio_files", exist_ok=True)
    yield
    await close_db()


app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered healthcare middleware connecting Doctors, Insurers, and Patients",
    version="1.0.0",
    lifespan=lifespan,
)

cors_origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins or ["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/audio", StaticFiles(directory="audio_files"), name="audio")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(doctor.router, prefix="/api/doctor", tags=["Doctor - Smart Scribe"])
app.include_router(insurer.router, prefix="/api/insurer", tags=["Insurer - Clearinghouse"])
app.include_router(patient.router, prefix="/api/patient", tags=["Patient - Care Companion"])
app.include_router(hospital.router, prefix="/api/hospital", tags=["Hospital - Admin"])


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": settings.APP_NAME}
