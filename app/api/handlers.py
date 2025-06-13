from fastapi import FastAPI, Request, status
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse

from app.domain.exceptions.base_exceptions import AppError


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register custom exception handlers for the FastAPI application.
    """

    @app.exception_handler(AppError)
    def app_exception_handler(request: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": "error",
                "code": exc.code,
                "detail": exc.detail,
            },
        )

    @app.exception_handler(RequestValidationError)
    def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "status": "error",
                "code": "validation_error",
                "detail": exc.errors(),
            },
        )

    @app.exception_handler(HTTPException)
    def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        if exc.status_code == status.HTTP_401_UNAUTHORIZED:
            return JSONResponse(
                headers=getattr(exc, "headers", None),
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "status": "error",
                    "code": "not_authenticated",
                    "detail": "You are not authenticated. "
                    "Please provide a valid authentication token to access this resource.",
                },
            )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": "error",
                "code": "http_error",
                "message": exc.detail,
            },
        )
