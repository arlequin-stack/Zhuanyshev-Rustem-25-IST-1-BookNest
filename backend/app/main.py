import logging
import time
import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.routers import auth, authors, books, genres, loans, wishlist

app = FastAPI(title=settings.app_name, version="1.0.0", docs_url="/api/docs", openapi_url="/api/openapi.json")
logger = logging.getLogger("booknest.requests")
app.add_middleware(CORSMiddleware, allow_origins=settings.origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.middleware("http")
async def request_context(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id
    started = time.perf_counter()
    response = await call_next(request)
    elapsed = time.perf_counter() - started
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{elapsed:.4f}"
    logger.info("request_id=%s method=%s path=%s status=%s duration=%.4f", request_id, request.method, request.url.path, response.status_code, elapsed)
    return response

@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, exc: RequestValidationError):
    details = [{key: value for key, value in error.items() if key != "ctx"} for error in exc.errors()]
    return JSONResponse(status_code=422, content={"code": "validation_error", "message": "Проверьте введённые данные", "details": details, "request_id": request.state.request_id})

@app.exception_handler(HTTPException)
async def http_error(request: Request, exc: HTTPException):
    code = {401: "unauthorized", 403: "forbidden", 404: "not_found", 409: "conflict"}.get(exc.status_code, "http_error")
    return JSONResponse(status_code=exc.status_code, headers=exc.headers, content={"code": code, "message": str(exc.detail), "details": None, "request_id": request.state.request_id})

@app.get("/health", tags=["system"])
def health():
    return {"status": "ok"}

for router in (auth.router, books.router, authors.router, genres.router, loans.router, wishlist.router):
    app.include_router(router, prefix="/api/v1")


# The Render image contains the compiled React application in /app/static.
# During backend-only development and tests this directory is absent, so the
# API keeps working exactly as before.
static_dir = Path(__file__).resolve().parent.parent / "static"
if static_dir.is_dir():
    static_root = static_dir.resolve()
    assets_dir = static_root / "assets"

    if assets_dir.is_dir():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="frontend-assets")

    @app.get("/", include_in_schema=False)
    def frontend_index():
        return FileResponse(static_root / "index.html")

    @app.get("/{full_path:path}", include_in_schema=False)
    def frontend_spa(full_path: str):
        requested_file = (static_root / full_path).resolve()
        if requested_file.is_file() and static_root in requested_file.parents:
            return FileResponse(requested_file)
        return FileResponse(static_root / "index.html")

