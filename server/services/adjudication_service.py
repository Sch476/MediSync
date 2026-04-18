"""Auto-Adjudication Rule Engine — Python-based claim processing.

No paid APIs. Pure business logic + JSON rules for Indian healthcare claims.
Checks ICD-10 codes, policy limits, room rent caps, and standard procedures.
"""
from typing import List, Tuple
from datetime import datetime


# Standard Indian health insurance rules (configurable JSON-like structure)
ADJUDICATION_RULES = {
    # Room rent caps by policy tier (INR per day)
    "room_rent_caps": {
        "basic": 2000,
        "standard": 4000,
        "premium": 8000,
        "super_premium": 15000,
    },
    # Auto-approve: common procedures that don't need manual review
    "auto_approve_icd_codes": [
        "J06.9",   # Acute upper respiratory infection
        "K29.7",   # Gastritis
        "J18.9",   # Pneumonia
        "A09",     # Gastroenteritis
        "N39.0",   # Urinary tract infection
        "M54.5",   # Low back pain
        "J45.9",   # Asthma
        "E11.9",   # Type 2 diabetes (routine)
        "I10",     # Essential hypertension (routine)
        "K35.80",  # Acute appendicitis
    ],
    # Flag for manual review: complex or high-cost procedures
    "manual_review_icd_codes": [
        "C",        # All cancer codes (prefix)
        "Z51",      # Chemotherapy
        "I21",      # Acute myocardial infarction
        "I63",      # Cerebral infarction
        "K80",      # Gallstone surgery
        "N20",      # Kidney stones (surgical)
    ],
    # Standard policy limits
    "max_claim_amount": {
        "basic": 300000,      # 3 lakh
        "standard": 500000,   # 5 lakh
        "premium": 1000000,   # 10 lakh
        "super_premium": 2500000,  # 25 lakh
    },
    # Pre-auth required procedures
    "pre_auth_required": [
        "surgery", "chemotherapy", "dialysis", "transplant",
        "joint replacement", "cardiac", "angioplasty", "bypass",
    ],
    # Excluded items (commonly not covered in Indian health insurance)
    "excluded_items": [
        "cosmetic", "dental", "spectacles", "hearing aid",
        "vitamins", "supplements", "fertility", "ivf",
    ],
    # Waiting period conditions (in days from policy start)
    "waiting_period_conditions": {
        "pre_existing": 730,    # 2 years
        "maternity": 540,       # 18 months
        "hernia": 365,          # 1 year
        "cataract": 365,
        "joint_replacement": 730,
    },
}


def get_policy_tier(policy_number: str) -> str:
    """Determine policy tier from policy number. In production, this queries the policy DB."""
    # Mock: derive tier from policy number prefix
    if policy_number.startswith("PREM"):
        return "premium"
    elif policy_number.startswith("STD"):
        return "standard"
    elif policy_number.startswith("SUP"):
        return "super_premium"
    return "standard"  # default


def adjudicate_claim(claim: dict) -> dict:
    """Run the auto-adjudication rule engine on a claim.

    Returns adjudication result with status, approved amount, and reason codes.
    """
    flags: List[str] = []
    rejections: List[str] = []
    adjustments: List[dict] = []
    approved_amount = claim.get("total_amount", 0)

    policy_tier = get_policy_tier(claim.get("policy_number", ""))

    # Rule 1: Check claim amount against policy limit
    max_amount = ADJUDICATION_RULES["max_claim_amount"].get(policy_tier, 500000)
    if approved_amount > max_amount:
        flags.append(f"Claim amount Rs {approved_amount} exceeds policy limit Rs {max_amount}")
        approved_amount = max_amount

    # Rule 2: Room rent cap check
    room_type = (claim.get("room_type") or "").lower()
    if room_type in ("private", "deluxe", "suite"):
        cap = ADJUDICATION_RULES["room_rent_caps"].get(policy_tier, 4000)
        for item in claim.get("items", []):
            if item.get("category") == "room":
                if item["amount"] > cap:
                    excess = item["amount"] - cap
                    flags.append(f"Room rent Rs {item['amount']}/day exceeds cap Rs {cap}/day. Excess: Rs {excess}")
                    approved_amount -= excess

    # Rule 3: Check for excluded items
    for item in claim.get("items", []):
        desc_lower = item.get("description", "").lower()
        for excluded in ADJUDICATION_RULES["excluded_items"]:
            if excluded in desc_lower:
                rejections.append(f"Excluded item: {item['description']} (policy exclusion: {excluded})")
                approved_amount -= item.get("amount", 0)

    # Rule 4: ICD code validation
    icd_codes = claim.get("icd_codes", [])
    needs_manual_review = False

    for code in icd_codes:
        # Check if code requires manual review (complex procedures)
        for review_prefix in ADJUDICATION_RULES["manual_review_icd_codes"]:
            if code.startswith(review_prefix):
                needs_manual_review = True
                flags.append(f"ICD code {code} requires manual review (complex procedure)")

    # Rule 5: Pre-authorization check
    diagnosis_lower = claim.get("diagnosis", "").lower()
    for procedure in ADJUDICATION_RULES["pre_auth_required"]:
        if procedure in diagnosis_lower:
            flags.append(f"Pre-authorization required for: {procedure}")
            needs_manual_review = True

    # Rule 6: Determine final status
    approved_amount = max(0, approved_amount)

    if rejections and not flags:
        status = "rejected"
        notes = f"Rejected: {'; '.join(rejections)}"
    elif needs_manual_review or len(flags) > 2:
        status = "flagged"
        notes = f"Flagged for manual review. {'; '.join(flags)}"
    elif flags:
        status = "flagged"
        notes = f"Auto-approved with adjustments. {'; '.join(flags)}"
    elif all(code in ADJUDICATION_RULES["auto_approve_icd_codes"] for code in icd_codes) and icd_codes:
        status = "approved"
        notes = "Auto-approved: standard procedure with valid ICD codes"
    else:
        status = "approved"
        notes = "Auto-approved: within policy limits"

    return {
        "status": status,
        "approved_amount": round(approved_amount, 2),
        "adjudication_notes": notes,
        "flag_reasons": flags,
        "rejection_reason": "; ".join(rejections) if rejections else None,
        "adjudicated_at": datetime.utcnow(),
    }
