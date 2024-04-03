import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import api_router


def create_app():
    app = FastAPI(
        title="Content Management API",
        description="A comprehensive API for content interaction and data processing.",
        version="1.0",
        docs_url="/api-docs",
        openapi_url="/api/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix="/api")

    @app.get("/")
    def health_check():
        return {
            "status": "healthy",
            "message": "API operational. Visit /api-docs for docs.",
        }

    return app
