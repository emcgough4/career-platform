from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.routes.contact import router as contact_router
from app.routes.portfolio import router as portfolio_router
from app.routes.public import router as public_router


app = FastAPI(title="Career Platform")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
def root() -> RedirectResponse:
    return RedirectResponse(url="/about")


app.include_router(public_router)
app.include_router(portfolio_router)
app.include_router(contact_router)
