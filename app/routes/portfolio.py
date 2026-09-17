from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.routes.public import get_session
from app.services.profile_service import load_public_profile

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/portfolio", response_class=HTMLResponse)
def portfolio_page(request: Request, session: Session = Depends(get_session)):
    context, fallback = load_public_profile(session)
    return templates.TemplateResponse(
        request=request, name="portfolio.html", context={**context, "fallback": fallback}
    )


@router.get("/projects/{project_id}", response_class=HTMLResponse)
def project_detail_page(request: Request, project_id: int, session: Session = Depends(get_session)):
    context, fallback = load_public_profile(session)
    project = next((item for item in context["projects"] if item["id"] == project_id), None)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return templates.TemplateResponse(
        request=request,
        name="project_detail.html",
        context={"project": project, "profile": context["profile"], "fallback": fallback},
    )
