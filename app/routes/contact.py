from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.routes.public import get_session
from app.services.profile_service import load_public_profile

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/contact", response_class=HTMLResponse)
def contact_page(request: Request, session: Session = Depends(get_session)):
    context, fallback = load_public_profile(session)
    return templates.TemplateResponse(
        request=request, name="contact.html", context={**context, "fallback": fallback}
    )
