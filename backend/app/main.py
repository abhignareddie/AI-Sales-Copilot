from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.exceptions import http_exception_handler, validation_exception_handler, general_exception_handler
from app.core.logging import logger
from app.middleware.logging import RequestLoggingMiddleware
from app.api.v1.router import api_router
from app.redis.client import close_redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"{settings.APP_NAME} v{settings.APP_VERSION} starting...")
    from app.database.base import Base
    from app.database.session import engine
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables initialized successfully.")
    except Exception as e:
        logger.error(f"Database table initialization failed: {e}")
    yield
    await close_redis()
    logger.info(f"{settings.APP_NAME} shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI Sales Copilot - Intelligent Next Best Action Platform",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)

# Exception Handlers
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Routes
app.include_router(api_router, prefix=settings.API_PREFIX)


# Advanced Production Health Checks
@app.get("/health")
async def health_check():
    """Full detailed system health report."""
    from sqlalchemy.sql import text
    from app.database.session import async_session_factory
    from app.redis.client import get_redis
    from app.rag.vector_service import VectorService

    db_status = "healthy"
    redis_status = "healthy"
    chroma_status = "healthy"

    # 1. Test Database
    try:
        async with async_session_factory() as session:
            await session.execute(text("SELECT 1"))
    except Exception as e:
        logger.error(f"Health check DB error: {e}")
        db_status = "unhealthy"

    # 2. Test Redis
    try:
        r = await get_redis()
        await r.ping()
    except Exception as e:
        logger.error(f"Health check Redis error: {e}")
        redis_status = "unhealthy"

    # 3. Test ChromaDB
    try:
        v = VectorService()
        if not v.client or not v.client.heartbeat():
            chroma_status = "unhealthy"
    except Exception as e:
        logger.error(f"Health check ChromaDB error: {e}")
        chroma_status = "unhealthy"

    overall = "healthy" if all(s == "healthy" for s in [db_status, redis_status, chroma_status]) else "unhealthy"

    return {
        "status": overall,
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "dependencies": {
            "database": db_status,
            "redis": redis_status,
            "chromadb": chroma_status
        }
    }

@app.get("/live")
async def liveness_probe():
    """Minimal liveness verification for orchestrators."""
    return {"status": "alive"}

@app.get("/ready")
async def readiness_probe(db_status: dict = Depends(health_check)):
    """Readiness probe checking dependencies."""
    if db_status["status"] != "healthy":
        raise HTTPException(status_code=503, detail="System not ready")
    return {"status": "ready"}

