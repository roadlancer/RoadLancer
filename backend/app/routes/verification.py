from fastapi import APIRouter, Depends, HTTPException, Header
from typing import Optional
from datetime import datetime, timezone
from pydantic import BaseModel
from app.database import db

router = APIRouter(prefix="/verification", tags=["verification"])


async def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = authorization.replace("Bearer ", "")

    session = await db.session.find_unique(where={"token": token})
    if not session:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    now = datetime.now(timezone.utc)
    expires = session.expiresAt
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    if expires < now:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    user = await db.user.find_unique(where={"id": session.userId})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    if getattr(user, "suspended", False):
        raise HTTPException(status_code=403, detail="Account suspended")

    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "role": user.role,
    }


async def get_admin_user(authorization: Optional[str] = Header(None)):
    user = await get_current_user(authorization)
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


class DriverVerificationRequest(BaseModel):
    licenseNumber: str
    vehicleType: str
    vehicleNumber: str


class ShipperVerificationRequest(BaseModel):
    businessName: str
    gstNumber: str
    companyAddress: str


class RejectVerificationRequest(BaseModel):
    reason: Optional[str] = None


def verification_to_dict(v) -> dict:
    return {
        "id": v.id,
        "userId": v.userId,
        "licenseNumber": v.licenseNumber,
        "vehicleType": v.vehicleType,
        "vehicleNumber": v.vehicleNumber,
        "businessName": v.businessName,
        "gstNumber": v.gstNumber,
        "companyAddress": v.companyAddress,
        "status": v.status.value if hasattr(v.status, "value") else v.status,
        "reviewedBy": v.reviewedBy,
        "reviewedAt": v.reviewedAt.isoformat() if v.reviewedAt else None,
        "rejectionReason": v.rejectionReason,
        "createdAt": v.createdAt.isoformat() if v.createdAt else None,
    }


@router.get("/status")
async def get_verification_status(user: dict = Depends(get_current_user)):
    verification = await db.user_verifications.find_unique(where={"userId": user["id"]})
    if not verification:
        return {"status": "none", "verification": None}
    return {"status": verification_to_dict(verification)["status"], "verification": verification_to_dict(verification)}


@router.post("/submit/driver")
async def submit_driver_verification(
    body: DriverVerificationRequest,
    user: dict = Depends(get_current_user),
):
    if user["role"] != "driver":
        raise HTTPException(status_code=400, detail="Only drivers can submit driver verification")

    existing = await db.user_verifications.find_unique(where={"userId": user["id"]})
    if existing and (existing.status.value if hasattr(existing.status, "value") else existing.status) == "approved":
        raise HTTPException(status_code=400, detail="Already verified")

    if existing:
        updated = await db.user_verifications.update(
            where={"userId": user["id"]},
            data={
                "licenseNumber": body.licenseNumber,
                "vehicleType": body.vehicleType,
                "vehicleNumber": body.vehicleNumber,
                "status": "pending",
                "reviewedBy": None,
                "reviewedAt": None,
                "rejectionReason": None,
            },
        )
        return verification_to_dict(updated)

    created = await db.user_verifications.create(
        data={
            "userId": user["id"],
            "licenseNumber": body.licenseNumber,
            "vehicleType": body.vehicleType,
            "vehicleNumber": body.vehicleNumber,
        },
    )
    return verification_to_dict(created)


@router.post("/submit/shipper")
async def submit_shipper_verification(
    body: ShipperVerificationRequest,
    user: dict = Depends(get_current_user),
):
    if user["role"] != "shipper":
        raise HTTPException(status_code=400, detail="Only shippers can submit shipper verification")

    existing = await db.user_verifications.find_unique(where={"userId": user["id"]})
    if existing and (existing.status.value if hasattr(existing.status, "value") else existing.status) == "approved":
        raise HTTPException(status_code=400, detail="Already verified")

    if existing:
        updated = await db.user_verifications.update(
            where={"userId": user["id"]},
            data={
                "businessName": body.businessName,
                "gstNumber": body.gstNumber,
                "companyAddress": body.companyAddress,
                "status": "pending",
                "reviewedBy": None,
                "reviewedAt": None,
                "rejectionReason": None,
            },
        )
        return verification_to_dict(updated)

    created = await db.user_verifications.create(
        data={
            "userId": user["id"],
            "businessName": body.businessName,
            "gstNumber": body.gstNumber,
            "companyAddress": body.companyAddress,
        },
    )
    return verification_to_dict(created)


@router.get("/admin/list")
async def list_verifications(
    status: Optional[str] = None,
    search: Optional[str] = None,
    admin: dict = Depends(get_admin_user),
):
    where = {}
    if status and status in ("pending", "approved", "rejected"):
        where["status"] = status

    verifications = await db.user_verifications.find_many(where=where, order={"createdAt": "desc"})

    if search:
        user_ids = [v.userId for v in verifications]
        users = await db.user.find_many(where={"id": {"in": user_ids}})
        user_map = {u.id: u for u in users}
        search_lower = search.lower()
        verifications = [
            v for v in verifications
            if v.userId in user_map
            and (
                search_lower in (user_map[v.userId].name or "").lower()
                or search_lower in (user_map[v.userId].email or "").lower()
            )
        ]

    result = []
    for v in verifications:
        user = await db.user.find_unique(where={"id": v.userId})
        v_dict = verification_to_dict(v)
        v_dict["userName"] = user.name if user else None
        v_dict["userEmail"] = user.email if user else None
        v_dict["userRole"] = user.role if user else None
        result.append(v_dict)

    return result


@router.get("/admin/count")
async def verification_count(status: Optional[str] = None, admin: dict = Depends(get_admin_user)):
    where = {}
    if status and status in ("pending", "approved", "rejected"):
        where["status"] = status
    else:
        where["status"] = "pending"
    count = await db.user_verifications.count(where=where)
    return {"count": count}


@router.post("/admin/{verification_id}/approve")
async def approve_verification(
    verification_id: str,
    admin: dict = Depends(get_admin_user),
):
    verification = await db.user_verifications.find_unique(where={"id": verification_id})
    if not verification:
        raise HTTPException(status_code=404, detail="Verification not found")

    current_status = verification.status.value if hasattr(verification.status, "value") else verification.status
    if current_status != "pending":
        raise HTTPException(status_code=400, detail="Verification is not pending")

    updated = await db.user_verifications.update(
        where={"id": verification_id},
        data={
            "status": "approved",
            "reviewedBy": admin["id"],
            "reviewedAt": datetime.now(timezone.utc),
        },
    )
    return verification_to_dict(updated)


@router.post("/admin/{verification_id}/reject")
async def reject_verification(
    verification_id: str,
    body: RejectVerificationRequest,
    admin: dict = Depends(get_admin_user),
):
    verification = await db.user_verifications.find_unique(where={"id": verification_id})
    if not verification:
        raise HTTPException(status_code=404, detail="Verification not found")

    current_status = verification.status.value if hasattr(verification.status, "value") else verification.status
    if current_status != "pending":
        raise HTTPException(status_code=400, detail="Verification is not pending")

    updated = await db.user_verifications.update(
        where={"id": verification_id},
        data={
            "status": "rejected",
            "reviewedBy": admin["id"],
            "reviewedAt": datetime.now(timezone.utc),
            "rejectionReason": body.reason,
        },
    )
    return verification_to_dict(updated)
