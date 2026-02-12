from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from core.config import settings
from db.database import engine, Base
from routers import system, pages, workflows

# Create Tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

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
