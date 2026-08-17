from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import orders, products
from app.core.config import get_settings
from app.db.init_db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            origin.strip()
            for origin in settings.frontend_origins.split(",")
            if origin.strip()
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.mount("/assets", StaticFiles(directory=settings.assets_dir), name="assets")
    app.include_router(products.router, prefix=settings.api_prefix)
    app.include_router(orders.router, prefix=settings.api_prefix)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    frontend_dist_dir = Path(settings.frontend_dist_dir)
    frontend_index = frontend_dist_dir / "index.html"
    if frontend_index.exists():
        app.mount(
            "/static",
            StaticFiles(directory=frontend_dist_dir / "static"),
            name="frontend-static",
        )

        @app.get("/favicon.svg", include_in_schema=False)
        def serve_favicon() -> FileResponse:
            return FileResponse(frontend_dist_dir / "favicon.svg")

        @app.get("/icons.svg", include_in_schema=False)
        def serve_icons() -> FileResponse:
            return FileResponse(frontend_dist_dir / "icons.svg")

        @app.get("/", include_in_schema=False)
        @app.get("/{full_path:path}", include_in_schema=False)
        def serve_frontend(full_path: str = "") -> FileResponse:
            return FileResponse(frontend_index)

    return app


app = create_app()
