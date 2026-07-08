from fastapi import APIRouter, HTTPException, Header
from typing import Optional
from datetime import datetime, timezone
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

    role_raw = getattr(user, "role", "driver")
    role_str = role_raw.value if hasattr(role_raw, "value") else role_raw

    if role_str != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "role": role_str,
    }
