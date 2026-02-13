from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi.responses import JSONResponse
from groq import Groq

from db.database import get_db, WorkflowRun
from core.schemas import KeyValidationRequest, WorkflowRunRead
from core.logging_config import get_logger
from typing import List

router = APIRouter()
logger = get_logger(__name__)

@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error("Health check failed", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

@router.post("/validate-key")
def validate_key(request: KeyValidationRequest):
    """Sync def — Groq SDK call is blocking, so FastAPI runs this in a threadpool."""
    try:
        test_client = Groq(api_key=request.api_key)
        test_client.models.list()
        logger.info("API key validated successfully")
        return {"valid": True}
    except Exception:
        logger.warning("API key validation failed")
        return JSONResponse(
            status_code=401, 
            content={"valid": False, "error": "Invalid API Key or connection failed"}
        )

@router.get("/runs", response_model=List[WorkflowRunRead])
def read_runs(skip: int = 0, limit: int = 5, db: Session = Depends(get_db)):
    runs = db.query(WorkflowRun).order_by(WorkflowRun.created_at.desc()).offset(skip).limit(limit).all()
    return runs

@router.get("/templates")
def get_templates():
    from core.templates import PREDEFINED_TEMPLATES
    return PREDEFINED_TEMPLATES

