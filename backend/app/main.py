from dotenv import load_dotenv
load_dotenv()

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.routes import shipments, auth
from app.middleware import RequestLoggingMiddleware, RateLimitMiddleware
from app.database import connect_db, disconnect_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    yield
    await disconnect_db()


app = FastAPI(
    title="RoadLancer API",
    description="AI-Powered Transportation Management System",
    version="1.0.0",
    lifespan=lifespan,
)

# Order matters: outermost middleware runs first
import os
app.add_middleware(RequestLoggingMiddleware)
if os.getenv("ENV") == "production":
    app.add_middleware(RateLimitMiddleware, max_requests=60, window_seconds=60)
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
