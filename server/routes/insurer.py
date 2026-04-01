"""Insurer/TPA routes — Clearinghouse module.

Handles: claim listing, auto-adjudication, manual review, approve/reject actions, analytics.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, Literal
from datetime import datetime
from bson import ObjectId

from middleware.auth_middleware import require_role
from database import get_db
from services.adjudication_service import adjudicate_claim

router = APIRouter()

insurer_role = require_role(["insurer"])


@router.get("/claims")
async def list_claims(
    status: Optional[str] = Query(None, description="Filter by status: pending, approved, rejected, flagged"),
    limit: int = Query(50, le=200),
    current_user: dict = Depends(insurer_role),
):
    """List all insurance claims, optionally filtered by status."""
    db = get_db()
    query = {}
    if status:
        query["status"] = status

    claims = await db.claims.find(query).sort("submitted_at", -1).to_list(limit)

    for claim in claims:
        claim["id"] = str(claim["_id"])
        del claim["_id"]

    return claims


@router.get("/claims/{claim_id}")
async def get_claim(claim_id: str, current_user: dict = Depends(insurer_role)):
    """Get detailed view of a specific claim."""
    db = get_db()
    claim = await db.claims.find_one({"_id": ObjectId(claim_id)})
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    claim["id"] = str(claim["_id"])
    del claim["_id"]

    # Also fetch the linked clinical note for full context
    if claim.get("clinical_note_id"):
        try:
            note = await db.clinical_notes.find_one({"_id": ObjectId(claim["clinical_note_id"])})
            if note:
                note["id"] = str(note["_id"])
                del note["_id"]
                claim["clinical_note"] = note
        except Exception:
            pass

    return claim


@router.post("/claims/{claim_id}/adjudicate")
async def auto_adjudicate_claim(claim_id: str, current_user: dict = Depends(insurer_role)):
    """Run auto-adjudication rule engine on a pending claim.

    Checks ICD-10 codes, policy limits, room rent caps, excluded items.
    Auto-approves standard procedures in <60s, flags complex ones for manual review.
    """
    db = get_db()
    claim = await db.claims.find_one({"_id": ObjectId(claim_id)})
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    if claim["status"] != "pending":
        raise HTTPException(status_code=400, detail=f"Claim already {claim['status']}")

    # Run the rule engine
    claim_dict = {**claim, "id": str(claim["_id"])}
    result = adjudicate_claim(claim_dict)

    # Update claim in MongoDB
    await db.claims.update_one(
        {"_id": ObjectId(claim_id)},
        {"$set": result},
    )

    return {"claim_id": claim_id, **result}


@router.post("/claims/{claim_id}/approve")
async def approve_claim(
    claim_id: str,
    approved_amount: Optional[float] = None,
    notes: Optional[str] = None,
    current_user: dict = Depends(insurer_role),
):
    """Manually approve a claim (for flagged claims requiring human review)."""
    db = get_db()
    claim = await db.claims.find_one({"_id": ObjectId(claim_id)})
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    update = {
        "status": "approved",
        "approved_amount": approved_amount or claim.get("total_amount", 0),
        "adjudication_notes": notes or "Manually approved by insurer",
        "adjudicated_at": datetime.utcnow(),
    }

    await db.claims.update_one({"_id": ObjectId(claim_id)}, {"$set": update})
    return {"claim_id": claim_id, **update}


@router.post("/claims/{claim_id}/reject")
async def reject_claim(
    claim_id: str,
    reason: str = "Claim does not meet policy criteria",
    current_user: dict = Depends(insurer_role),
):
    """Manually reject a claim with a reason."""
    db = get_db()
    claim = await db.claims.find_one({"_id": ObjectId(claim_id)})
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    update = {
        "status": "rejected",
        "rejection_reason": reason,
        "adjudication_notes": f"Rejected by insurer: {reason}",
        "approved_amount": 0,
        "adjudicated_at": datetime.utcnow(),
    }

    await db.claims.update_one({"_id": ObjectId(claim_id)}, {"$set": update})
    return {"claim_id": claim_id, **update}


@router.get("/analytics")
async def get_analytics(current_user: dict = Depends(insurer_role)):
    """Get claim analytics for the insurer dashboard charts."""
    db = get_db()

    # Count claims by status
    pipeline_status = [
        {"$group": {"_id": "$status", "count": {"$sum": 1}, "total_amount": {"$sum": "$total_amount"}}},
    ]
    status_stats = await db.claims.aggregate(pipeline_status).to_list(10)

    # Count claims by diagnosis (top 10)
    pipeline_diagnosis = [
        {"$group": {"_id": "$diagnosis", "count": {"$sum": 1}, "total_amount": {"$sum": "$total_amount"}}},
        {"$sort": {"count": -1}},
        {"$limit": 10},
    ]
    diagnosis_stats = await db.claims.aggregate(pipeline_diagnosis).to_list(10)

    # Monthly claims trend
    pipeline_monthly = [
        {"$group": {
            "_id": {"$dateToString": {"format": "%Y-%m", "date": "$submitted_at"}},
            "count": {"$sum": 1},
            "total_amount": {"$sum": "$total_amount"},
            "approved_amount": {"$sum": {"$ifNull": ["$approved_amount", 0]}},
        }},
        {"$sort": {"_id": 1}},
        {"$limit": 12},
    ]
    monthly_stats = await db.claims.aggregate(pipeline_monthly).to_list(12)

    # Total counts
    total_claims = await db.claims.count_documents({})
    pending_claims = await db.claims.count_documents({"status": "pending"})
    approved_claims = await db.claims.count_documents({"status": "approved"})
    rejected_claims = await db.claims.count_documents({"status": "rejected"})
    flagged_claims = await db.claims.count_documents({"status": "flagged"})

    return {
        "summary": {
            "total": total_claims,
            "pending": pending_claims,
            "approved": approved_claims,
            "rejected": rejected_claims,
            "flagged": flagged_claims,
        },
        "by_status": status_stats,
        "by_diagnosis": diagnosis_stats,
        "monthly_trend": monthly_stats,
    }


@router.post("/adjudicate-all-pending")
async def adjudicate_all_pending(current_user: dict = Depends(insurer_role)):
    """Batch auto-adjudicate all pending claims."""
    db = get_db()
    pending = await db.claims.find({"status": "pending"}).to_list(100)

    results = {"approved": 0, "rejected": 0, "flagged": 0, "total": len(pending)}

    for claim in pending:
        claim_dict = {**claim, "id": str(claim["_id"])}
        result = adjudicate_claim(claim_dict)
        await db.claims.update_one({"_id": claim["_id"]}, {"$set": result})
        results[result["status"]] += 1

    return results
