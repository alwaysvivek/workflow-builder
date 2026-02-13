from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
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

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

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
