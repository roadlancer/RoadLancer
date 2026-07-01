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

    user_status = getattr(user, "status", "approved")
    if user_status != "approved":
        status_msg = "Account pending approval. Please wait for admin approval." if user_status == "pending" else "Account has been rejected. Contact admin."
        raise HTTPException(status_code=403, detail=status_msg)

    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "phone": user.phone,
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
