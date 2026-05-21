"""Insurer/TPA routes — Clearinghouse module.

Handles: claim listing, auto-adjudication, manual review, approve/reject actions, analytics.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, Literal, List
from datetime import datetime
from bson import ObjectId
from pydantic import BaseModel

from middleware.auth_middleware import require_role
from database import get_db
from services.adjudication_service import adjudicate_claim

router = APIRouter()

insurer_role = require_role(["insurer"])


class BatchApproveRequest(BaseModel):
    claim_ids: List[str]
    notes: Optional[str] = None


class BatchRejectRequest(BaseModel):
    claim_ids: List[str]
    reason: str


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

    claim_dict = {**claim, "id": str(claim["_id"])}
    result = adjudicate_claim(claim_dict)

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
    if claim.get("status") in ("approved", "rejected"):
        raise HTTPException(status_code=400, detail=f"Claim is already {claim['status']} and cannot be changed.")

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
    if claim.get("status") in ("approved", "rejected"):
        raise HTTPException(status_code=400, detail=f"Claim is already {claim['status']} and cannot be changed.")

    update = {
        "status": "rejected",
        "rejection_reason": reason,
        "adjudication_notes": f"Rejected by insurer: {reason}",
        "approved_amount": 0,
        "adjudicated_at": datetime.utcnow(),
    }

    await db.claims.update_one({"_id": ObjectId(claim_id)}, {"$set": update})
    return {"claim_id": claim_id, **update}


@router.post("/claims/batch-approve")
async def batch_approve_claims(
    payload: BatchApproveRequest,
    current_user: dict = Depends(insurer_role),
):
    """Approve many adjudicated claims at once.

    Each claim is approved at its rule-engine-recommended amount. Flagged claims
    in the list are skipped (they need individual review).
    """
    if not payload.claim_ids:
        raise HTTPException(status_code=400, detail="No claim IDs provided")

    db = get_db()
    object_ids = [ObjectId(cid) for cid in payload.claim_ids]
    claims = await db.claims.find({"_id": {"$in": object_ids}}).to_list(len(object_ids))

    approved, skipped = [], []
    for claim in claims:
        cid = str(claim["_id"])
        if claim.get("status") != "adjudicated":
            skipped.append({"id": cid, "reason": f"Status is '{claim.get('status')}', not 'adjudicated'"})
            continue

        amount = claim.get("recommended_amount")
        if amount is None:
            amount = claim.get("total_amount", 0)

        await db.claims.update_one(
            {"_id": claim["_id"]},
            {"$set": {
                "status": "approved",
                "approved_amount": amount,
                "adjudication_notes": payload.notes or f"Batch-approved at recommended amount ₹{amount}",
                "adjudicated_at": datetime.utcnow(),
            }},
        )
        approved.append(cid)

    return {"approved": approved, "skipped": skipped, "approved_count": len(approved)}


@router.post("/claims/batch-reject")
async def batch_reject_claims(
    payload: BatchRejectRequest,
    current_user: dict = Depends(insurer_role),
):
    """Reject many adjudicated claims at once with a shared reason.

    Flagged claims in the list are skipped.
    """
    if not payload.claim_ids:
        raise HTTPException(status_code=400, detail="No claim IDs provided")
    if not payload.reason.strip():
        raise HTTPException(status_code=400, detail="Rejection reason is required")

    db = get_db()
    object_ids = [ObjectId(cid) for cid in payload.claim_ids]
    claims = await db.claims.find({"_id": {"$in": object_ids}}).to_list(len(object_ids))

    rejected, skipped = [], []
    for claim in claims:
        cid = str(claim["_id"])
        if claim.get("status") != "adjudicated":
            skipped.append({"id": cid, "reason": f"Status is '{claim.get('status')}', not 'adjudicated'"})
            continue

        await db.claims.update_one(
            {"_id": claim["_id"]},
            {"$set": {
                "status": "rejected",
                "rejection_reason": payload.reason,
                "adjudication_notes": f"Batch-rejected by insurer: {payload.reason}",
                "approved_amount": 0,
                "adjudicated_at": datetime.utcnow(),
            }},
        )
        rejected.append(cid)

    return {"rejected": rejected, "skipped": skipped, "rejected_count": len(rejected)}


@router.get("/analytics")
async def get_analytics(current_user: dict = Depends(insurer_role)):
    """Get claim analytics for the insurer dashboard charts."""
    db = get_db()

    pipeline_status = [
        {"$group": {"_id": "$status", "count": {"$sum": 1}, "total_amount": {"$sum": "$total_amount"}}},
    ]
    status_stats = await db.claims.aggregate(pipeline_status).to_list(10)

    pipeline_diagnosis = [
        {"$group": {"_id": "$diagnosis", "count": {"$sum": 1}, "total_amount": {"$sum": "$total_amount"}}},
        {"$sort": {"count": -1}},
        {"$limit": 10},
    ]
    diagnosis_stats = await db.claims.aggregate(pipeline_diagnosis).to_list(10)

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

    total_claims = await db.claims.count_documents({})
    pending_claims = await db.claims.count_documents({"status": "pending"})
    adjudicated_claims = await db.claims.count_documents({"status": "adjudicated"})
    approved_claims = await db.claims.count_documents({"status": "approved"})
    rejected_claims = await db.claims.count_documents({"status": "rejected"})
    flagged_claims = await db.claims.count_documents({"status": "flagged"})

    total_amount_result = await db.claims.aggregate([
        {"$group": {"_id": None, "total": {"$sum": "$total_amount"}}}
    ]).to_list(1)
    total_amount = total_amount_result[0]["total"] if total_amount_result else 0

    return {
        "total_claims": total_claims,
        "total_amount": total_amount,
        "pending": pending_claims,
        "adjudicated": adjudicated_claims,
        "approved": approved_claims,
        "rejected": rejected_claims,
        "flagged": flagged_claims,
        "top_diagnoses": [
            {"diagnosis": d["_id"] or "Unknown", "count": d["count"]}
            for d in diagnosis_stats
        ],
        "monthly_trend": [
            {"month": m["_id"], "count": m["count"], "amount": m["total_amount"]}
            for m in monthly_stats
        ],
    }


@router.post("/adjudicate-all-pending")
async def adjudicate_all_pending(current_user: dict = Depends(insurer_role)):
    """Run the rule engine on all pending claims.

    Produces "adjudicated" claims (with a recommendation) and "flagged" claims.
    The insurer still makes the final approve/reject decision — either one at a
    time, or via /claims/batch-approve and /claims/batch-reject.
    """
    db = get_db()
    pending = await db.claims.find({"status": "pending"}).to_list(100)

    results = {"adjudicated": 0, "flagged": 0, "total": len(pending)}

    for claim in pending:
        claim_dict = {**claim, "id": str(claim["_id"])}
        result = adjudicate_claim(claim_dict)
        await db.claims.update_one({"_id": claim["_id"]}, {"$set": result})
        results[result["status"]] = results.get(result["status"], 0) + 1

    return results
