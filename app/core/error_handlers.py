from fastapi import Request, FastAPI, status
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import RequestValidationError
from fastapi.exceptions import RequestValidationError, HTTPException as FastAPIHTTPException
from starlette.exceptions import HTTPException as StarletteHTTPException

def register_error_handlers(app: FastAPI):
    # Handles HTTPExceptions (including those raised in endpoints)
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    # Handles FastAPI's own HTTPException (rare, but future-proof)
    @app.exception_handler(FastAPIHTTPException)
    async def fastapi_http_exception_handler(request: Request, exc: FastAPIHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    # Handles validation errors (like wrong/missing fields)
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": exc.errors()},
        )
