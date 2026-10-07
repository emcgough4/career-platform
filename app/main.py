from fastapi import FastAPI, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.db import SessionLocal
from app.routes.contact import router as contact_router
from app.routes.portfolio import router as portfolio_router
from app.routes.public import router as public_router
from app.services.profile_service import load_public_profile
from app.templating import templates


app = FastAPI(title="Career Platform")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.exception_handler(StarletteHTTPException)
async def not_found_page(request: Request, exc: StarletteHTTPException):
    """Render a site page for 404s when a browser asks for HTML; keep JSON otherwise."""
    if exc.status_code != 404 or "text/html" not in request.headers.get("accept", ""):
        return await http_exception_handler(request, exc)
    session = SessionLocal()
    try:
        context, fallback = load_public_profile(session)
    finally:
        session.close()
    return templates.TemplateResponse(
        request=request, name="404.html", context={**context, "fallback": fallback}, status_code=404
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
def root() -> RedirectResponse:
    return RedirectResponse(url="/about")


app.include_router(public_router)
app.include_router(portfolio_router)
app.include_router(contact_router)
