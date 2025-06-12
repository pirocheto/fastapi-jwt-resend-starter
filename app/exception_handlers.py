from fastapi import FastAPI, Request, status
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse

from app.core.exceptions import APIException


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register custom exception handlers for the FastAPI application.
    """

    @app.exception_handler(APIException)
    def app_exception_handler(request: Request, exc: APIException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": "error",
                "code": exc.code,
                "message": exc.message,
            },
        )

    @app.exception_handler(RequestValidationError)
    def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "status": "error",
                "code": "validation_error",
                "message": "Validation error",
                "detail": exc.errors(),
            },
        )

    @app.exception_handler(HTTPException)
    def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        if exc.status_code == status.HTTP_401_UNAUTHORIZED:
            headers = getattr(exc, "headers", None)
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "status": "error",
                    "code": "not_authenticated",
                    "message": "You are not authenticated. "
                    "Please provide a valid authentication token to access this resource.",
                },
                headers=headers,
            )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": "error",
                "code": "http_error",
                "message": exc.detail,
            },
        )
