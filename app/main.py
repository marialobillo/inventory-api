from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from .api import build_products_router
from .errors import AlreadyExists, NotFound

def create_app() -> FastAPI:
    app = FastAPI(title="Inventory API (FastAPI)")

    @app.exception_handler(RequestValidationError)
    async def handle_validation(_req: Request, exc: RequestValidationError):
        details = []
        for e in exc.errors():
            msg = e.get("msg")
            loc = ".".join([str(x) for x in e.get("loc", [])])
            details.append(f"{loc}: {msg}" if loc else msg)
        return JSONResponse(status_code=400, content={"error": "ValidationError", "details": details})

    @app.exception_handler(AlreadyExists)
    async def handle_conflict(_req: Request, _exc: AlreadyExists):
        return JSONResponse(status_code=409, content={"error": "AlreadyExists"})

    @app.exception_handler(NotFound)
    async def handle_notfound(_req: Request, _exc: NotFound):
        return JSONResponse(status_code=404, content={"error": "NotFound"})

    app.include_router(build_products_router())

    @app.get("/health")
    async def health():
        return {"ok": True}

    return app

app = create_app()
