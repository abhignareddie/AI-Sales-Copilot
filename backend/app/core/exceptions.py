from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.core.logging import logger


from typing import Any

def sanitize_json(data: Any) -> Any:
    if isinstance(data, dict):
        return {k: sanitize_json(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_json(v) for v in data]
    elif isinstance(data, bytes):
        return data.decode('utf-8', errors='ignore')
    return data


async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"HTTP {exc.status_code}: {exc.detail} | {request.method} {request.url}")
    return JSONResponse(
        status_code=exc.status_code,
        content=sanitize_json({
            "success": False,
            "error": exc.detail,
            "status_code": exc.status_code,
        }),
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Validation error: {exc.errors()} | {request.method} {request.url}")
    return JSONResponse(
        status_code=422,
        content=sanitize_json({
            "success": False,
            "error": "Validation Error",
            "details": exc.errors(),
            "status_code": 422,
        }),
    )


async def general_exception_handler(request: Request, exc: Exception):
    logger.error(
        f"Internal Server Error: {str(exc)} | {request.method} {request.url}",
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content=sanitize_json({
            "success": False,
            "error": "Internal Server Error",
            "status_code": 500,
        }),
    )
