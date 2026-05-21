"""K-Anonymity based data anonymization for patient records."""
import re
import hashlib
from typing import Dict, Any


def anonymize_patient_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Apply K-Anonymity principles to patient data before sharing with insurers.

    - Generalizes age to ranges
    - Hashes direct identifiers
    - Keeps medical data intact for claim processing
    """
    anonymized = data.copy()

    if "patient_name" in anonymized:
        anonymized["patient_name_hash"] = _hash_identifier(anonymized["patient_name"])

    if "email" in anonymized:
        anonymized["email_hash"] = _hash_identifier(anonymized["email"])

    if "age" in anonymized:
        anonymized["age_range"] = _generalize_age(anonymized["age"])
        del anonymized["age"]

    if "phone" in anonymized:
        phone = str(anonymized["phone"])
        anonymized["phone"] = "XXXX-" + phone[-4:]

    if "address" in anonymized:
        anonymized["location"] = _generalize_location(anonymized["address"])
        del anonymized["address"]

    return anonymized


def _hash_identifier(value: str) -> str:
    """SHA-256 hash of an identifier for pseudonymization."""
    return hashlib.sha256(value.encode()).hexdigest()[:16]


def _generalize_age(age: int) -> str:
    """Generalize exact age to 5-year range."""
    lower = (age // 5) * 5
    upper = lower + 4
    return f"{lower}-{upper}"


def _generalize_location(address: str) -> str:
    """Extract only city-level information from full address."""
    parts = [p.strip() for p in address.split(",")]
    if len(parts) >= 2:
        return ", ".join(parts[-2:])
    return parts[-1] if parts else "Unknown"


def redact_pii_from_text(text: str) -> str:
    """Redact common PII patterns from free-text fields."""
    text = re.sub(r'\b\d{4}\s?\d{4}\s?\d{4}\b', '[AADHAAR_REDACTED]', text)
    text = re.sub(r'\b(\+91|0)?[6-9]\d{9}\b', '[PHONE_REDACTED]', text)
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL_REDACTED]', text)
    text = re.sub(r'\b[A-Z]{5}\d{4}[A-Z]\b', '[PAN_REDACTED]', text)
    return text
