from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.routes.public import get_session
from app.services.profile_service import load_public_profile
from app.templating import templates

router = APIRouter()


@router.get("/contact", response_class=HTMLResponse)
def contact_page(request: Request, session: Session = Depends(get_session)):
    context, fallback = load_public_profile(session)
    return templates.TemplateResponse(
        request=request, name="contact.html", context={**context, "fallback": fallback}
    )
