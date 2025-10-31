from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.core.logging import setup_logging
from app.api.v1.endpoints import diagnosis, health

# Настройка логирования
setup_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Plant Disease Diagnosis with Reasoning Component",
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(
    diagnosis.router,
    prefix=f"{settings.API_V1_STR}/diagnosis",
    tags=["diagnosis"]
)
app.include_router(
    health.router,
    prefix=f"{settings.API_V1_STR}/health",
    tags=["health"]
)

@app.get("/")
async def root():
    return {
        "message": "Plant Disease Reasoning API",
        "version": settings.VERSION,
        "docs": "/docs"
    }
