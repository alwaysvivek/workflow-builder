from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import time

from core.config import settings
from core.logging_config import setup_logging, get_logger
from db.database import engine, Base
from routers import system, pages, workflows

# Initialize structured JSON logging
setup_logging()
logger = get_logger(__name__)

# Create Tables
Base.metadata.create_all(bind=engine)

# Rate limiter (uses client IP by default)
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS — restrict to same-origin; add explicit origins if frontend is hosted separately
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "https://workflow-builder-db32.onrender.com",
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "x-groq-api-key"],
)

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data:; "
        "connect-src 'self'"
    )
    return response

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - start) * 1000, 2)
    logger.info(
        "Request completed",
        extra={
            "method": request.method,
            "path": str(request.url.path),
            "status_code": response.status_code,
            "duration_ms": duration_ms,
        },
    )
    return response


# Mount Static
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include Routers
app.include_router(pages.router)
app.include_router(system.router)
app.include_router(workflows.router)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    errors = []
    for error in exc.errors():
        if error['type'] == 'enum':
            errors.append(f"Invalid action '{error['input']}'. Allowed actions: {error['ctx']['expected']}")
        elif error['type'] == 'value_error':
             errors.append(error['msg'])
        else:
            errors.append(f"{error['loc'][-1]}: {error['msg']}")
            
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation Error", "errors": errors},
    )

