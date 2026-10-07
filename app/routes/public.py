from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.services.profile_service import load_public_profile
from app.templating import templates

router = APIRouter()


def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@router.get("/about", response_class=HTMLResponse)
def about_page(request: Request, session: Session = Depends(get_session)):
    context, fallback = load_public_profile(session)
    return templates.TemplateResponse(
        request=request, name="about.html", context={**context, "fallback": fallback}
    )


@router.get("/resume", response_class=HTMLResponse)
def resume_page(request: Request, session: Session = Depends(get_session)):
    context, fallback = load_public_profile(session)
    return templates.TemplateResponse(
        request=request, name="resume.html", context={**context, "fallback": fallback}
    )
