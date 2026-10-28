"""Composition root: middleware, routes, error mapping, storage lifecycle."""
import sqlite3
import importlib
import pkgutil
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException
from .errors import ValidationError
from .middleware import NoStoreMiddleware
from .database import Database
from . import features


def error_response(status, code, message, fields=None):
    return JSONResponse(status_code=status, content={"error": {"code": code, "message": message, "fields": fields or {}}})


def create_app(db_path=None, frontend_dist=None):
    database = Database(db_path or Path(__file__).resolve().parents[1] / "data" / "still.sqlite3")
    stores = []

    @asynccontextmanager
    async def lifespan(app):
        try:
            database.initialize()
            for store in stores:
                store.initialize()
        except (sqlite3.Error, OSError):
            # Keep static navigation/Emergency usable; API operations report 503.
            pass
        yield

    app = FastAPI(title="inspire API", lifespan=lifespan)
    app.add_middleware(NoStoreMiddleware)
    for module in pkgutil.iter_modules(features.__path__):
        if module.ispkg:
            feature = importlib.import_module(f"{features.__name__}.{module.name}")
            store = feature.register(app, database)
            if store is not None:
                stores.append(store)

    @app.exception_handler(ValidationError)
    async def domain_error(_request, exc):
        return error_response(422, "validation_error", str(exc), exc.fields)

    @app.exception_handler(RequestValidationError)
    async def shape_error(_request, exc):
        fields = {str(issue["loc"][-1]): "Check this field's value and type." for issue in exc.errors()}
        return error_response(422, "validation_error", "Check the highlighted fields.", fields)

    @app.exception_handler(HTTPException)
    async def http_error(_request, exc):
        return error_response(exc.status_code, "not_found" if exc.status_code == 404 else "http_error", str(exc.detail))

    @app.exception_handler(sqlite3.Error)
    async def storage_error(_request, _exc):
        return error_response(503, "storage_unavailable", "Saved records are unavailable. Try again shortly.")

    @app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
    def missing_api(path: str):
        raise HTTPException(404, "API route not found.")

    dist = Path(frontend_dist) if frontend_dist else Path(__file__).resolve().parents[2] / "frontend" / "dist"
    if dist.is_dir():
        app.mount("/", StaticFiles(directory=dist, html=True), name="frontend")

    return app


app = create_app()
