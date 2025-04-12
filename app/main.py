import logging
import os
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api.routes import router as api_router
from app.core.config import get_settings
from app.monitoring.metrics import register_metrics

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Storybook AI application")
    os.makedirs(settings.DATA_DIR, exist_ok=True)

    try:
        from app.llm.embeddings import get_vector_store
        _ = get_vector_store()
        logger.info("Vector store loaded successfully")
    except Exception as e:
        logger.error(f"Error loading vector store: {e}")

    yield
    logger.info("Shutting down Storybook AI application")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    description="Storybook AI - Harry Potter Books 1-4 knowledge base"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://storybookharry.netlify.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred"}
    )


app.include_router(api_router, prefix="/api")

if settings.ENABLE_METRICS:
    register_metrics(app)


@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "Storybook AI - Harry Potter Books 1-4 knowledge base"
    }

@app.get("/health")
async def root_health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
