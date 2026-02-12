from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/help", response_class=HTMLResponse)
async def read_help(request: Request):
    return templates.TemplateResponse("help.html", {"request": request})

@router.get("/history", response_class=HTMLResponse)
async def read_history(request: Request):
    return templates.TemplateResponse("history.html", {"request": request})

@router.get("/status", response_class=HTMLResponse)
async def read_status(request: Request):
    return templates.TemplateResponse("status.html", {"request": request})
