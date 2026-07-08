from fastapi import APIRouter, Depends, HTTPException, Header
from typing import Optional
from datetime import datetime, timezone
from app.database import db

router = APIRouter()


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
        raise HTTPException(status_code=403, detail="Account suspended. Contact admin.")

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
        "phone": user.phone,
        "status": user_status,
    }


@router.get("/me")
async def me(user: dict = Depends(get_current_user)):
    return user


@router.post("/sign-out")
async def sign_out(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = authorization.replace("Bearer ", "")
    await db.session.delete(where={"token": token})
    return {"message": "Signed out"}
