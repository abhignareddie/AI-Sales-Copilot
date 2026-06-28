import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging import logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(
            f"{request.method} {request.url.path} | "
            f"Status: {response.status_code} | "
            f"Time: {process_time:.3f}s"
        )
        response.headers["X-Process-Time"] = f"{process_time:.3f}"
        return response
