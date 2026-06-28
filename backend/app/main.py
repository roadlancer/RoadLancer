from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import shipments, auth

app = FastAPI(
    title="RoadLancer API",
    description="AI-Powered Transportation Management System",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(shipments.router, prefix="/api/shipments", tags=["shipments"])


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "roadlancer-backend"}
