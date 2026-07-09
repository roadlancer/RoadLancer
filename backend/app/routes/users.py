from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from pydantic import BaseModel
from app.database import db
from app.routes.admin import get_admin_user

router = APIRouter(prefix="/admin/users", tags=["users"])


class SuspendRequest(BaseModel):
    suspended: bool


class ReviewRequest(BaseModel):
    reason: Optional[str] = None


def user_to_dict(u) -> dict:
    role_val = u.role.value if hasattr(u.role, "value") else u.role
    status_raw = getattr(u, "status", "approved")
    status_val = status_raw.value if hasattr(status_raw, "value") else status_raw
    return {
        "id": u.id,
        "name": u.name,
        "email": u.email,
        "role": role_val,
        "phone": u.phone,
        "suspended": getattr(u, "suspended", False),
        "status": status_val,
        "created_at": (u.createdAt if isinstance(u.createdAt, str) else u.createdAt.isoformat()) if u.createdAt else None,
    }


@router.get("")
async def list_users(
    role: Optional[str] = None,
    search: Optional[str] = None,
    sort_field: Optional[str] = None,
    sort_order: Optional[str] = "desc",
    admin: dict = Depends(get_admin_user),
):
    where = {}
    if role and role in ("driver", "shipper", "admin"):
        where["role"] = role

    order_dict = {}
    valid_sorts = {"created_at": "createdAt", "name": "name", "email": "email", "role": "role", "status": "status"}
    if sort_field and sort_field in valid_sorts:
        order_dict = {valid_sorts[sort_field]: "asc" if (sort_order or "").lower() == "asc" else "desc"}
    else:
        order_dict = {"createdAt": "desc"}

    if search:
        users = await db.user.find_many(where=where, order=order_dict)
        search_lower = search.lower()
        users = [
            u for u in users
            if search_lower in (u.name or "").lower()
            or search_lower in (u.email or "").lower()
        ]
    else:
        users = await db.user.find_many(where=where, order=order_dict)

    verifications = await db.query_raw('SELECT user_id as "userId", status FROM user_verifications')
    verif_map = {v.get("userId") if isinstance(v, dict) else v.userId: ((v.get("status").value if hasattr(v.get("status"), "value") else v.get("status")) if isinstance(v, dict) else (v.status.value if hasattr(v.status, "value") else v.status)) for v in verifications}

    result = []
    for u in users:
        d = user_to_dict(u)
        d["verification_status"] = verif_map.get(u.id, "none")
        result.append(d)
    return result


@router.get("/pending/list")
async def list_pending_users(
    search: Optional[str] = None,
    admin: dict = Depends(get_admin_user),
):
    where = {"status": "pending"}

    if search:
        users = await db.user.find_many(where=where)
        search_lower = search.lower()
        users = [
            u for u in users
            if search_lower in (u.name or "").lower()
            or search_lower in (u.email or "").lower()
        ]
    else:
        users = await db.user.find_many(where=where, order={"createdAt": "desc"})

    verifications = await db.query_raw('SELECT user_id as "userId", status FROM user_verifications')
    verif_map = {v.get("userId") if isinstance(v, dict) else v.userId: ((v.get("status").value if hasattr(v.get("status"), "value") else v.get("status")) if isinstance(v, dict) else (v.status.value if hasattr(v.status, "value") else v.status)) for v in verifications}

    result = []
    for u in users:
        d = user_to_dict(u)
        d["verification_status"] = verif_map.get(u.id, "none")
        result.append(d)
    return result


@router.get("/pending/count")
async def pending_users_count(admin: dict = Depends(get_admin_user)):
    count = await db.user.count(where={"status": "pending"})
    return {"count": count}


@router.get("/{user_id}")
async def get_user(user_id: str, admin: dict = Depends(get_admin_user)):
    user = await db.user.find_unique(where={"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user_to_dict(user)


@router.post("/{user_id}/suspend")
async def suspend_user(
    user_id: str,
    body: SuspendRequest,
    admin: dict = Depends(get_admin_user),
):
    if user_id == admin["id"]:
        raise HTTPException(status_code=400, detail="Cannot suspend yourself")

    user = await db.user.find_unique(where={"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.role == "admin":
        raise HTTPException(status_code=400, detail="Cannot suspend another admin")

    updated = await db.user.update(
        where={"id": user_id},
        data={"suspended": body.suspended},
    )

    if body.suspended:
        await db.session.delete_many(where={"userId": user_id})

    return user_to_dict(updated)


@router.post("/{user_id}/approve")
async def approve_user(
    user_id: str,
    admin: dict = Depends(get_admin_user),
):
    user = await db.user.find_unique(where={"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.status != "pending":
        raise HTTPException(status_code=400, detail="User is not pending approval")

    updated = await db.user.update(
        where={"id": user_id},
        data={"status": "approved"},
    )
    return user_to_dict(updated)


@router.post("/{user_id}/reject")
async def reject_user(
    user_id: str,
    body: ReviewRequest,
    admin: dict = Depends(get_admin_user),
):
    user = await db.user.find_unique(where={"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.status != "pending":
        raise HTTPException(status_code=400, detail="User is not pending approval")

    updated = await db.user.update(
        where={"id": user_id},
        data={"status": "rejected"},
    )

    # Revoke any sessions
    await db.session.delete_many(where={"userId": user_id})

    return user_to_dict(updated)
