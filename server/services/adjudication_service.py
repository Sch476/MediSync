"""Auto-Adjudication Rule Engine — Python-based claim processing.

No paid APIs. Pure business logic + JSON rules for Indian healthcare claims.
Checks ICD-10 codes, policy limits, room rent caps, and standard procedures.
"""
from typing import List, Tuple
from datetime import datetime


ADJUDICATION_RULES = {
    "room_rent_caps": {
        "basic": 2000,
        "standard": 4000,
        "premium": 8000,
        "super_premium": 15000,
    },
    "auto_approve_icd_codes": [
        "J06.9",
        "K29.7",
        "J18.9",
        "A09",
        "N39.0",
        "M54.5",
        "J45.9",
        "E11.9",
        "I10",
        "K35.80",
    ],
    "manual_review_icd_codes": [
        "C",
        "Z51",
        "I21",
        "I63",
        "K80",
        "N20",
    ],
    "max_claim_amount": {
        "basic": 300000,
        "standard": 500000,
        "premium": 1000000,
        "super_premium": 2500000,
    },
    "pre_auth_required": [
        "surgery", "chemotherapy", "dialysis", "transplant",
        "joint replacement", "cardiac", "angioplasty", "bypass",
    ],
    "excluded_items": [
        "cosmetic", "dental", "spectacles", "hearing aid",
        "vitamins", "supplements", "fertility", "ivf",
    ],
    "waiting_period_conditions": {
        "pre_existing": 730,
        "maternity": 540,
        "hernia": 365,
        "cataract": 365,
        "joint_replacement": 730,
    },
}


def get_policy_tier(policy_number: str) -> str:
    """Determine policy tier from policy number. In production, this queries the policy DB."""
    if policy_number.startswith("PREM"):
        return "premium"
    elif policy_number.startswith("STD"):
        return "standard"
    elif policy_number.startswith("SUP"):
        return "super_premium"
    return "standard"


def adjudicate_claim(claim: dict) -> dict:
    """Run the auto-adjudication rule engine on a claim.

    IMPORTANT: The rule engine no longer auto-approves or auto-rejects claims.
    It produces one of two statuses:
      - "adjudicated" — rules ran cleanly; a recommendation is attached ("approve" or
        "reject") along with a recommended amount. The insurer makes the final call
        (individually or via batch actions).
      - "flagged" — complex case that needs human review (cancer, cardiac, pre-auth,
        or many concurrent flags). Insurer must handle these one by one.
    """
    flags: List[str] = []
    rejections: List[str] = []
    recommended_amount = claim.get("total_amount", 0)

    policy_tier = get_policy_tier(claim.get("policy_number", ""))

    max_amount = ADJUDICATION_RULES["max_claim_amount"].get(policy_tier, 500000)
    if recommended_amount > max_amount:
        flags.append(f"Claim amount ₹{recommended_amount} exceeds policy limit ₹{max_amount}")
        recommended_amount = max_amount

    room_type = (claim.get("room_type") or "").lower()
    if room_type in ("private", "deluxe", "suite"):
        cap = ADJUDICATION_RULES["room_rent_caps"].get(policy_tier, 4000)
        for item in claim.get("items", []):
            if item.get("category") == "room":
                if item["amount"] > cap:
                    excess = item["amount"] - cap
                    flags.append(f"Room rent ₹{item['amount']}/day exceeds cap ₹{cap}/day. Excess: ₹{excess}")
                    recommended_amount -= excess

    for item in claim.get("items", []):
        desc_lower = item.get("description", "").lower()
        for excluded in ADJUDICATION_RULES["excluded_items"]:
            if excluded in desc_lower:
                rejections.append(f"Excluded item: {item['description']} (policy exclusion: {excluded})")
                recommended_amount -= item.get("amount", 0)

    icd_codes = claim.get("icd_codes", [])
    needs_manual_review = False

    for code in icd_codes:
        for review_prefix in ADJUDICATION_RULES["manual_review_icd_codes"]:
            if code.startswith(review_prefix):
                needs_manual_review = True
                flags.append(f"ICD code {code} requires manual review (complex procedure)")

    diagnosis_lower = claim.get("diagnosis", "").lower()
    for procedure in ADJUDICATION_RULES["pre_auth_required"]:
        if procedure in diagnosis_lower:
            flags.append(f"Pre-authorization required for: {procedure}")
            needs_manual_review = True

    recommended_amount = max(0, recommended_amount)

    if needs_manual_review or len(flags) > 2:
        status = "flagged"
        recommendation = None
        notes = f"Flagged for manual review. {'; '.join(flags)}"
    else:
        status = "adjudicated"
        if rejections and not flags:
            recommendation = "reject"
            notes = f"Recommended: Reject. Reason: {'; '.join(rejections)}"
        elif flags:
            recommendation = "approve"
            notes = f"Recommended: Approve with adjustments (₹{recommended_amount}). {'; '.join(flags)}"
        elif all(code in ADJUDICATION_RULES["auto_approve_icd_codes"] for code in icd_codes) and icd_codes:
            recommendation = "approve"
            notes = "Recommended: Approve — standard procedure with valid ICD codes"
        else:
            recommendation = "approve"
            notes = "Recommended: Approve — within policy limits"

    return {
        "status": status,
        "recommendation": recommendation,
        "recommended_amount": round(recommended_amount, 2),
        "adjudication_notes": notes,
        "flag_reasons": flags,
        "rejection_reason": "; ".join(rejections) if rejections else None,
        "adjudicated_at": datetime.utcnow(),
    }
