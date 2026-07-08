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

    user_status_raw = getattr(user, "status", "approved")
    user_status = user_status_raw.value if hasattr(user_status_raw, "value") else user_status_raw
    if user_status == "rejected":
        raise HTTPException(status_code=403, detail="Account has been rejected. Contact admin.")

    role_raw = getattr(user, "role", "driver")
    role_str = role_raw.value if hasattr(role_raw, "value") else role_raw

    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "role": role_str,
        "status": user_status,
    }


async def get_admin_user(authorization: Optional[str] = Header(None)):
    user = await get_current_user(authorization)
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


class DriverVerificationRequest(BaseModel):
    isEditRequest: Optional[bool] = False
    editReason: Optional[str] = None
    fullName: Optional[str] = None
    fatherName: Optional[str] = None
    dateOfBirth: Optional[str] = None
    bloodGroup: Optional[str] = None
    aadhaarLast4: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    emergencyContactName: Optional[str] = None
    emergencyContactPhone: Optional[str] = None
    profilePhoto: Optional[str] = None
    aadhaarPhoto: Optional[str] = None

    licenseNumber: Optional[str] = None
    dlExpiryDate: Optional[str] = None
    dlCategory: Optional[str] = None
    vehicleRegNumber: Optional[str] = None
    vehicleType: Optional[str] = None
    vehicleMakeModel: Optional[str] = None
    vehicleYear: Optional[int] = None
    insurancePolicyNumber: Optional[str] = None
    insuranceProvider: Optional[str] = None
    insuranceExpiryDate: Optional[str] = None
    pucCertificateNumber: Optional[str] = None
    pucExpiryDate: Optional[str] = None
    dlPhoto: Optional[str] = None
    rcBookPhoto: Optional[str] = None
    insurancePhoto: Optional[str] = None


class ShipperVerificationRequest(BaseModel):
    isEditRequest: Optional[bool] = False
    editReason: Optional[str] = None
    fullName: Optional[str] = None
    aadhaarLast4: Optional[str] = None
    phone: Optional[str] = None
    emergencyContactName: Optional[str] = None
    emergencyContactPhone: Optional[str] = None
    profilePhoto: Optional[str] = None
    aadhaarPhoto: Optional[str] = None

    businessName: Optional[str] = None
    businessType: Optional[str] = None
    gstNumber: Optional[str] = None
    panNumber: Optional[str] = None
    registeredAddress: Optional[str] = None
    annualTurnover: Optional[str] = None
    yearsInBusiness: Optional[int] = None
    primaryGoodsCategory: Optional[str] = None
    gstCertPhoto: Optional[str] = None
    panCardPhoto: Optional[str] = None
    businessRegPhoto: Optional[str] = None


class RejectVerificationRequest(BaseModel):
    reason: Optional[str] = None


def parse_date(date_str: Optional[str]) -> Optional[datetime]:
    if not date_str:
        return None
    try:
        if "T" in date_str:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except Exception:
        return None


def format_dt(dt) -> Optional[str]:
    if not dt:
        return None
    if isinstance(dt, str):
        return dt
    return dt.isoformat() if hasattr(dt, "isoformat") else str(dt)


VERIFICATION_NO_PHOTOS_SELECT = {
    "id": True,
    "userId": True,
    "fullName": True,
    "fatherName": True,
    "dateOfBirth": True,
    "bloodGroup": True,
    "aadhaarLast4": True,
    "address": True,
    "phone": True,
    "emergencyContactName": True,
    "emergencyContactPhone": True,
    "licenseNumber": True,
    "dlExpiryDate": True,
    "dlCategory": True,
    "vehicleRegNumber": True,
    "vehicleType": True,
    "vehicleMakeModel": True,
    "vehicleYear": True,
    "insurancePolicyNumber": True,
    "insuranceProvider": True,
    "insuranceExpiryDate": True,
    "pucCertificateNumber": True,
    "pucExpiryDate": True,
    "businessName": True,
    "businessType": True,
    "gstNumber": True,
    "panNumber": True,
    "registeredAddress": True,
    "annualTurnover": True,
    "yearsInBusiness": True,
    "primaryGoodsCategory": True,
    "aiVerificationScore": True,
    "aiVerificationResult": True,
    "aiVerifiedAt": True,
    "aiAutoRejected": True,
    "status": True,
    "reviewedBy": True,
    "reviewedAt": True,
    "rejectionReason": True,
    "createdAt": True,
    "updatedAt": True,
}


def verification_to_dict(v, include_photos: bool = False) -> dict:
    if not v:
        return {}
    get_val = lambda obj, k, default=None: obj.get(k, default) if isinstance(obj, dict) else getattr(obj, k, default)
    status_raw = get_val(v, "status", "pending")
    status_val = status_raw.value if hasattr(status_raw, "value") else status_raw

    data = {
        "id": get_val(v, "id"),
        "userId": get_val(v, "userId"),
        "fullName": get_val(v, "fullName"),
        "fatherName": get_val(v, "fatherName"),
        "dateOfBirth": format_dt(get_val(v, "dateOfBirth")),
        "bloodGroup": get_val(v, "bloodGroup"),
        "aadhaarLast4": get_val(v, "aadhaarLast4"),
        "address": get_val(v, "address"),
        "phone": get_val(v, "phone"),
        "emergencyContactName": get_val(v, "emergencyContactName"),
        "emergencyContactPhone": get_val(v, "emergencyContactPhone"),

        "licenseNumber": get_val(v, "licenseNumber"),
        "dlExpiryDate": format_dt(get_val(v, "dlExpiryDate")),
        "dlCategory": get_val(v, "dlCategory"),
        "vehicleRegNumber": get_val(v, "vehicleRegNumber"),
        "vehicleType": get_val(v, "vehicleType"),
        "vehicleMakeModel": get_val(v, "vehicleMakeModel"),
        "vehicleYear": get_val(v, "vehicleYear"),
        "insurancePolicyNumber": get_val(v, "insurancePolicyNumber"),
        "insuranceProvider": get_val(v, "insuranceProvider"),
        "insuranceExpiryDate": format_dt(get_val(v, "insuranceExpiryDate")),
        "pucCertificateNumber": get_val(v, "pucCertificateNumber"),
        "pucExpiryDate": format_dt(get_val(v, "pucExpiryDate")),

        "businessName": get_val(v, "businessName"),
        "businessType": get_val(v, "businessType"),
        "gstNumber": get_val(v, "gstNumber"),
        "panNumber": get_val(v, "panNumber"),
        "registeredAddress": get_val(v, "registeredAddress"),
        "annualTurnover": get_val(v, "annualTurnover"),
        "yearsInBusiness": get_val(v, "yearsInBusiness"),
        "primaryGoodsCategory": get_val(v, "primaryGoodsCategory"),

        "aiVerificationScore": get_val(v, "aiVerificationScore"),
        "aiVerificationResult": get_val(v, "aiVerificationResult"),
        "aiVerifiedAt": format_dt(get_val(v, "aiVerifiedAt")),
        "aiAutoRejected": get_val(v, "aiAutoRejected", False),

        "status": status_val,
        "reviewedBy": get_val(v, "reviewedBy"),
        "reviewedAt": format_dt(get_val(v, "reviewedAt")),
        "rejectionReason": get_val(v, "rejectionReason"),
        "createdAt": format_dt(get_val(v, "createdAt")),
    }
    if include_photos:
        data.update({
            "profilePhoto": get_val(v, "profilePhoto"),
            "aadhaarPhoto": get_val(v, "aadhaarPhoto"),
            "dlPhoto": get_val(v, "dlPhoto"),
            "rcBookPhoto": get_val(v, "rcBookPhoto"),
            "insurancePhoto": get_val(v, "insurancePhoto"),
            "gstCertPhoto": get_val(v, "gstCertPhoto"),
            "panCardPhoto": get_val(v, "panCardPhoto"),
            "businessRegPhoto": get_val(v, "businessRegPhoto"),
        })
    return data


@router.get("/status")
async def get_verification_status(include_photos: bool = False, user: dict = Depends(get_current_user)):
    if not include_photos:
        rows = await db.query_raw(
            'SELECT id, user_id as "userId", full_name as "fullName", father_name as "fatherName", '
            'date_of_birth as "dateOfBirth", blood_group as "bloodGroup", aadhaar_last4 as "aadhaarLast4", '
            'address, phone, emergency_contact_name as "emergencyContactName", '
            'emergency_contact_phone as "emergencyContactPhone", license_number as "licenseNumber", '
            'dl_expiry_date as "dlExpiryDate", dl_category as "dlCategory", '
            'vehicle_reg_number as "vehicleRegNumber", vehicle_type as "vehicleType", '
            'vehicle_make_model as "vehicleMakeModel", vehicle_year as "vehicleYear", '
            'insurance_policy_number as "insurancePolicyNumber", insurance_provider as "insuranceProvider", '
            'insurance_expiry_date as "insuranceExpiryDate", puc_certificate_number as "pucCertificateNumber", '
            'puc_expiry_date as "pucExpiryDate", business_name as "businessName", '
            'business_type as "businessType", gst_number as "gstNumber", pan_number as "panNumber", '
            'registered_address as "registeredAddress", annual_turnover as "annualTurnover", '
            'years_in_business as "yearsInBusiness", primary_goods_category as "primaryGoodsCategory", '
            'ai_verification_score as "aiVerificationScore", ai_verification_result as "aiVerificationResult", '
            'ai_verified_at as "aiVerifiedAt", ai_auto_rejected as "aiAutoRejected", status, '
            'reviewed_by as "reviewedBy", reviewed_at as "reviewedAt", rejection_reason as "rejectionReason", '
            'created_at as "createdAt" FROM user_verifications WHERE user_id = $1',
            user["id"]
        )
        verification = rows[0] if rows else None
    else:
        verification = await db.user_verifications.find_unique(where={"userId": user["id"]})
    if not verification:
        return {"status": "none", "verification": None}
    v_dict = verification_to_dict(verification, include_photos=include_photos)
    return {"status": v_dict["status"], "verification": v_dict}


@router.post("/submit/driver")
async def submit_driver_verification(
    body: DriverVerificationRequest,
    user: dict = Depends(get_current_user),
):
    if user["role"] != "driver":
        raise HTTPException(status_code=400, detail="Only drivers can submit driver verification")

    existing = await db.user_verifications.find_unique(where={"userId": user["id"]})
    if existing and (existing.status.value if hasattr(existing.status, "value") else existing.status) == "approved":
        if not body.isEditRequest:
            raise HTTPException(status_code=400, detail="Already verified. Use Request Profile Edit option to submit changes.")

    update_data = {
        "fullName": body.fullName,
        "fatherName": body.fatherName,
        "dateOfBirth": parse_date(body.dateOfBirth),
        "bloodGroup": body.bloodGroup,
        "aadhaarLast4": body.aadhaarLast4,
        "address": body.address,
        "phone": body.phone,
        "emergencyContactName": body.emergencyContactName,
        "emergencyContactPhone": body.emergencyContactPhone,
        "profilePhoto": body.profilePhoto,
        "aadhaarPhoto": body.aadhaarPhoto,

        "licenseNumber": body.licenseNumber,
        "dlExpiryDate": parse_date(body.dlExpiryDate),
        "dlCategory": body.dlCategory,
        "vehicleRegNumber": body.vehicleRegNumber,
        "vehicleType": body.vehicleType,
        "vehicleMakeModel": body.vehicleMakeModel,
        "vehicleYear": body.vehicleYear,
        "insurancePolicyNumber": body.insurancePolicyNumber,
        "insuranceProvider": body.insuranceProvider,
        "insuranceExpiryDate": parse_date(body.insuranceExpiryDate),
        "pucCertificateNumber": body.pucCertificateNumber,
        "pucExpiryDate": parse_date(body.pucExpiryDate),
        "dlPhoto": body.dlPhoto,
        "rcBookPhoto": body.rcBookPhoto,
        "insurancePhoto": body.insurancePhoto,

        "status": "pending",
        "reviewedBy": None,
        "reviewedAt": None,
        "rejectionReason": f"[PROFILE EDIT REQUEST] {body.editReason or 'User requested profile update'}" if body.isEditRequest else None,
    }

    if existing:
        updated = await db.user_verifications.update(where={"userId": user["id"]}, data=update_data)
        return verification_to_dict(updated, include_photos=True)

    create_data = {"user": {"connect": {"id": user["id"]}}}
    create_data.update(update_data)
    created = await db.user_verifications.create(data=create_data)
    return verification_to_dict(created, include_photos=True)


@router.post("/submit/shipper")
async def submit_shipper_verification(
    body: ShipperVerificationRequest,
    user: dict = Depends(get_current_user),
):
    if user["role"] != "shipper":
        raise HTTPException(status_code=400, detail="Only shippers can submit shipper verification")

    existing = await db.user_verifications.find_unique(where={"userId": user["id"]})
    if existing and (existing.status.value if hasattr(existing.status, "value") else existing.status) == "approved":
        if not body.isEditRequest:
            raise HTTPException(status_code=400, detail="Already verified. Use Request Profile Edit option to submit changes.")

    update_data = {
        "fullName": body.fullName,
        "aadhaarLast4": body.aadhaarLast4,
        "phone": body.phone,
        "emergencyContactName": body.emergencyContactName,
        "emergencyContactPhone": body.emergencyContactPhone,
        "profilePhoto": body.profilePhoto,
        "aadhaarPhoto": body.aadhaarPhoto,

        "businessName": body.businessName,
        "businessType": body.businessType,
        "gstNumber": body.gstNumber,
        "panNumber": body.panNumber,
        "registeredAddress": body.registeredAddress,
        "annualTurnover": body.annualTurnover,
        "yearsInBusiness": body.yearsInBusiness,
        "primaryGoodsCategory": body.primaryGoodsCategory,
        "gstCertPhoto": body.gstCertPhoto,
        "panCardPhoto": body.panCardPhoto,
        "businessRegPhoto": body.businessRegPhoto,

        "status": "pending",
        "reviewedBy": None,
        "reviewedAt": None,
        "rejectionReason": f"[PROFILE EDIT REQUEST] {body.editReason or 'User requested profile update'}" if body.isEditRequest else None,
    }

    if existing:
        updated = await db.user_verifications.update(where={"userId": user["id"]}, data=update_data)
        return verification_to_dict(updated, include_photos=True)

    create_data = {"user": {"connect": {"id": user["id"]}}}
    create_data.update(update_data)
    created = await db.user_verifications.create(data=create_data)
    return verification_to_dict(created, include_photos=True)


@router.get("/documents/{verification_id}")
async def get_verification_documents(
    verification_id: str,
    admin: dict = Depends(get_admin_user),
):
    verification = await db.user_verifications.find_unique(where={"id": verification_id})
    if not verification:
        raise HTTPException(status_code=404, detail="Verification not found")
    return verification_to_dict(verification, include_photos=True)


@router.get("/admin/list")
async def list_verifications(
    status: Optional[str] = None,
    search: Optional[str] = None,
    admin: dict = Depends(get_admin_user),
):
    if status and status in ("pending", "approved", "rejected"):
        verifications = await db.query_raw(
            'SELECT id, user_id as "userId", full_name as "fullName", father_name as "fatherName", '
            'date_of_birth as "dateOfBirth", blood_group as "bloodGroup", aadhaar_last4 as "aadhaarLast4", '
            'address, phone, emergency_contact_name as "emergencyContactName", '
            'emergency_contact_phone as "emergencyContactPhone", license_number as "licenseNumber", '
            'dl_expiry_date as "dlExpiryDate", dl_category as "dlCategory", '
            'vehicle_reg_number as "vehicleRegNumber", vehicle_type as "vehicleType", '
            'vehicle_make_model as "vehicleMakeModel", vehicle_year as "vehicleYear", '
            'insurance_policy_number as "insurancePolicyNumber", insurance_provider as "insuranceProvider", '
            'insurance_expiry_date as "insuranceExpiryDate", puc_certificate_number as "pucCertificateNumber", '
            'puc_expiry_date as "pucExpiryDate", business_name as "businessName", '
            'business_type as "businessType", gst_number as "gstNumber", pan_number as "panNumber", '
            'registered_address as "registeredAddress", annual_turnover as "annualTurnover", '
            'years_in_business as "yearsInBusiness", primary_goods_category as "primaryGoodsCategory", '
            'ai_verification_score as "aiVerificationScore", ai_verification_result as "aiVerificationResult", '
            'ai_verified_at as "aiVerifiedAt", ai_auto_rejected as "aiAutoRejected", status, '
            'reviewed_by as "reviewedBy", reviewed_at as "reviewedAt", rejection_reason as "rejectionReason", '
            'created_at as "createdAt" FROM user_verifications WHERE status::text = $1 ORDER BY created_at DESC',
            status
        )
    else:
        verifications = await db.query_raw(
            'SELECT id, user_id as "userId", full_name as "fullName", father_name as "fatherName", '
            'date_of_birth as "dateOfBirth", blood_group as "bloodGroup", aadhaar_last4 as "aadhaarLast4", '
            'address, phone, emergency_contact_name as "emergencyContactName", '
            'emergency_contact_phone as "emergencyContactPhone", license_number as "licenseNumber", '
            'dl_expiry_date as "dlExpiryDate", dl_category as "dlCategory", '
            'vehicle_reg_number as "vehicleRegNumber", vehicle_type as "vehicleType", '
            'vehicle_make_model as "vehicleMakeModel", vehicle_year as "vehicleYear", '
            'insurance_policy_number as "insurancePolicyNumber", insurance_provider as "insuranceProvider", '
            'insurance_expiry_date as "insuranceExpiryDate", puc_certificate_number as "pucCertificateNumber", '
            'puc_expiry_date as "pucExpiryDate", business_name as "businessName", '
            'business_type as "businessType", gst_number as "gstNumber", pan_number as "panNumber", '
            'registered_address as "registeredAddress", annual_turnover as "annualTurnover", '
            'years_in_business as "yearsInBusiness", primary_goods_category as "primaryGoodsCategory", '
            'ai_verification_score as "aiVerificationScore", ai_verification_result as "aiVerificationResult", '
            'ai_verified_at as "aiVerifiedAt", ai_auto_rejected as "aiAutoRejected", status, '
            'reviewed_by as "reviewedBy", reviewed_at as "reviewedAt", rejection_reason as "rejectionReason", '
            'created_at as "createdAt" FROM user_verifications ORDER BY created_at DESC'
        )

    get_uid = lambda obj: obj.get("userId") if isinstance(obj, dict) else obj.userId
    all_user_ids = list(set(get_uid(v) for v in verifications))
    users = await db.user.find_many(where={"id": {"in": all_user_ids}})
    user_map = {u.id: u for u in users}

    if search:
        search_lower = search.lower()
        verifications = [
            v for v in verifications
            if get_uid(v) in user_map
            and (
                search_lower in (user_map[get_uid(v)].name or "").lower()
                or search_lower in (user_map[get_uid(v)].email or "").lower()
            )
        ]

    result = []
    for v in verifications:
        uid = get_uid(v)
        user = user_map.get(uid)
        v_dict = verification_to_dict(v, include_photos=False)
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
            "rejectionReason": None,
        },
    )
    if verification.userId and verification.fullName:
        update_user_data = {"name": verification.fullName}
        if verification.phone:
            update_user_data["phone"] = verification.phone
        try:
            await db.user.update(where={"id": verification.userId}, data=update_user_data)
        except Exception as e:
            print(f"Could not sync user table: {e}")
    return verification_to_dict(updated)


@router.post("/admin/{verification_id}/reset-pending")
async def reset_verification_to_pending(
    verification_id: str,
    admin: dict = Depends(get_admin_user),
):
    """Admin utility to soft-reset an approved or rejected verification back to pending."""
    verification = await db.user_verifications.find_unique(where={"id": verification_id})
    if not verification:
        raise HTTPException(status_code=404, detail="Verification not found")

    updated = await db.user_verifications.update(
        where={"id": verification_id},
        data={
            "status": "pending",
            "reviewedBy": None,
            "reviewedAt": None,
        },
    )
    return verification_to_dict(updated)


@router.post("/admin/reset-all-pending")
async def reset_all_verifications_to_pending(
    admin: dict = Depends(get_admin_user),
):
    """Admin utility to soft-reset all verification records back to pending so users can fill required data."""
    count = await db.user_verifications.update_many(
        where={},
        data={
            "status": "pending",
            "reviewedBy": None,
            "reviewedAt": None,
        },
    )
    return {"message": f"Reset {count} records to pending", "count": count}


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
