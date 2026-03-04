import logging
import os

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from app.auth.dependencies import get_current_user
from app.database import engine, Base
from app.models import User
from app.schemas import UserResponse
from app.routes import auth, upload, rag, review, export
from app.services.chroma_service import init_chroma

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Almabase Assignment API")

# ── CORS ─────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Static files for exports ─────────────────────────────────
os.makedirs("uploads", exist_ok=True)
os.makedirs("exports", exist_ok=True)
os.makedirs("chroma_data", exist_ok=True)

app.include_router(auth.router)
app.include_router(upload.router)
app.include_router(rag.router)
app.include_router(review.router)
app.include_router(export.router)

# Mount AFTER routers — mounted sub-apps shadow routes with similar prefixes
app.mount("/exports", StaticFiles(directory="exports"), name="exports")


@app.on_event("startup")
async def on_startup():
    # Create DB tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # Initialize ChromaDB
    init_chroma()


@app.get("/health")
async def health_check():
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "Database connected"}
    except Exception as e:
        return {"status": "Database connection failed", "error": str(e)}


@app.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    return user
