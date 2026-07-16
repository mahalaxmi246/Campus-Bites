from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.exceptions import AppError, app_error_handler
from app.routers import admin,auth, canteen, menu

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
app.include_router(menu.router, prefix="/api/v1/menu", tags=["menu"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])
app.include_router(canteen.router, prefix="/api/v1/canteens", tags=["canteens"])
# More routers get included here starting Week 5+ (orders, ...)


@app.get("/")
def root():
    return {"service": settings.app_name, "status": "running"}


@app.get("/health")
def health():
    return {"status": "ok"}