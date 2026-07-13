import os
import httpx
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter()

AUTH_SERVER_URL = os.getenv("BETTER_AUTH_URL", "http://localhost:3000")


@router.post("/ai/polish")
async def proxy_polish(request: Request):
    try:
        body = await request.json()
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{AUTH_SERVER_URL}/api/auth/ai/polish",
                json=body,
                headers={"Content-Type": "application/json"},
            )
            return JSONResponse(content=resp.json(), status_code=resp.status_code)
    except httpx.TimeoutException:
        return JSONResponse(content={"error": "Auth server timeout"}, status_code=504)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=502)


@router.post("/ai/summarize")
async def proxy_summarize(request: Request):
    try:
        body = await request.json()
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{AUTH_SERVER_URL}/api/auth/ai/summarize",
                json=body,
                headers={"Content-Type": "application/json"},
            )
            return JSONResponse(content=resp.json(), status_code=resp.status_code)
    except httpx.TimeoutException:
        return JSONResponse(content={"error": "Auth server timeout"}, status_code=504)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=502)


@router.post("/ai/classify")
async def proxy_classify(request: Request):
    try:
        body = await request.json()
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{AUTH_SERVER_URL}/api/auth/ai/classify",
                json=body,
                headers={"Content-Type": "application/json"},
            )
            return JSONResponse(content=resp.json(), status_code=resp.status_code)
    except httpx.TimeoutException:
        return JSONResponse(content={"error": "Auth server timeout"}, status_code=504)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=502)
