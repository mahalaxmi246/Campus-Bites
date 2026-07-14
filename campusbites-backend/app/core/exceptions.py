from fastapi import Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    """
    Base exception for all app-level (non-validation) errors. Every route
    should raise this instead of a raw HTTPException, so every error
    response follows the same {"error": {"code", "message"}} shape
    documented in docs/api-contract.md.
    """

    def __init__(self, code: str, message: str, status_code: int = 400):
        self.code = code
        self.message = message
        self.status_code = status_code


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.code, "message": exc.message}},
    )