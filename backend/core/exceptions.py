from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import logging


def http_exception_handler(request: Request, exc: HTTPException):
    logging.warning(
        f"HTTP {exc.status_code} | {request.method} {request.url.path} | {exc.detail}"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP Error",
            "detail": exc.detail,
        },
    )


def unhandled_exception_handler(request: Request, exc: Exception):
    logging.error(
        f"Unhandled exception | {request.method} {request.url.path}",
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": "Ocorreu um erro inesperado no servidor.",
        },
    )
