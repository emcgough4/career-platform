from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.routes.contact import router as contact_router
from app.routes.portfolio import router as portfolio_router
from app.routes.public import router as public_router


app = FastAPI(title="Career Platform")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", response_class=PlainTextResponse)
def root() -> str:
    return f"{settings.app_name} is running"


app.include_router(public_router)
app.include_router(portfolio_router)
app.include_router(contact_router)
