"""
FastAPI application entry point for SimpleIQ Backend
"""

from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.api.v1 import auth, data, queries, dashboards
from app.core.config import settings
from app.core.database import create_db_tables


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Manage application lifecycle events
    """
    # Startup
    print(f"Starting {settings.PROJECT_NAME} v{settings.APP_VERSION}")
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Debug mode: {settings.DEBUG}")
    
    # Create database tables
    await create_db_tables()
    
    yield
    
    # Shutdown
    print(f"Shutting down {settings.PROJECT_NAME}")


# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.APP_VERSION,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",
    lifespan=lifespan,
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

if settings.ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*.simpleiq.io", "simpleiq.io"],
    )

# Include API routers
app.include_router(auth.router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["auth"])
app.include_router(data.router, prefix=f"{settings.API_V1_PREFIX}/data", tags=["data"])
app.include_router(
    queries.router, prefix=f"{settings.API_V1_PREFIX}/queries", tags=["queries"]
)
app.include_router(
    dashboards.router,
    prefix=f"{settings.API_V1_PREFIX}/dashboards",
    tags=["dashboards"],
)


@app.get("/")
async def root() -> dict[str, Any]:
    """
    Root endpoint
    """
    return {
        "message": "Welcome to SimpleIQ API",
        "version": settings.APP_VERSION,
        "docs": f"{settings.API_V1_PREFIX}/docs",
    }


@app.get("/health")
async def health_check() -> dict[str, Any]:
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }