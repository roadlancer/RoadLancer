from fastapi import APIRouter, Depends, HTTPException, Header
from typing import Optional
from datetime import datetime, timezone

router = APIRouter()


async def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = authorization.replace("Bearer ", "")

    from prisma import Prisma

    db = Prisma()
    await db.connect()
    try:
        session = await db.session.find_unique(where={"token": token})
        if not session:
            raise HTTPException(status_code=401, detail="Invalid session")

        now = datetime.now(timezone.utc)
        expires = session.expiresAt
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        if expires < now:
            raise HTTPException(status_code=401, detail="Session expired")

        user = await db.user.find_unique(where={"id": session.userId})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        return {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role,
            "phone": user.phone,
        }
    finally:
        await db.disconnect()


@router.get("/me")
async def me(user: dict = Depends(get_current_user)):
    return user
