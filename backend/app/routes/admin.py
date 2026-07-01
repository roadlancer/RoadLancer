from fastapi import APIRouter, Depends, HTTPException, Header
from typing import Optional
from datetime import datetime, timezone
from pydantic import BaseModel
from app.database import db

router = APIRouter(prefix="/admin", tags=["admin"])


async def get_admin_user(authorization: Optional[str] = Header(None)):
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

    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "role": user.role,
    }


class SuspendRequest(BaseModel):
    suspended: bool


def user_to_dict(u) -> dict:
    return {
        "id": u.id,
        "name": u.name,
        "email": u.email,
        "role": u.role,
        "phone": u.phone,
        "suspended": getattr(u, "suspended", False),
        "status": getattr(u, "status", "approved"),
        "created_at": u.createdAt.isoformat() if u.createdAt else None,
    }


@router.get("/users")
async def list_users(
    role: Optional[str] = None,
    search: Optional[str] = None,
    admin: dict = Depends(get_admin_user),
):
    where = {}
    if role and role in ("driver", "shipper", "admin"):
        where["role"] = role

    if search:
        users = await db.user.find_many(where=where)
        search_lower = search.lower()
        users = [
            u for u in users
            if search_lower in (u.name or "").lower()
            or search_lower in (u.email or "").lower()
        ]
    else:
        users = await db.user.find_many(where=where)

    return [user_to_dict(u) for u in users]


@router.get("/users/{user_id}")
async def get_user(user_id: str, admin: dict = Depends(get_admin_user)):
    user = await db.user.find_unique(where={"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user_to_dict(user)


@router.post("/users/{user_id}/suspend")
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


@router.get("/users/pending/list")
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

    return [user_to_dict(u) for u in users]


@router.get("/users/pending/count")
async def pending_users_count(admin: dict = Depends(get_admin_user)):
    count = await db.user.count(where={"status": "pending"})
    return {"count": count}


class ReviewRequest(BaseModel):
    reason: Optional[str] = None


@router.post("/users/{user_id}/approve")
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


@router.post("/users/{user_id}/reject")
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
