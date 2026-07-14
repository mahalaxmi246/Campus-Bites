from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.exceptions import AppError, app_error_handler
from app.routers import auth

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(AppError, app_error_handler)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
# More routers get included here starting Day 9+ (menu, orders, ...)


@app.get("/")
def root():
    return {"service": settings.app_name, "status": "running"}


@app.get("/health")
def health():
    """Liveness check. A proper /ready (DB connectivity check) lands in Phase 2 (FR14)."""
    return {"status": "ok"}