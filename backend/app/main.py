from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import supabase


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        supabase.table("games").select("count").limit(1).execute()
        print("Supabase подключен")
    except Exception as e:
        print(f"Supabase ошибка: {e}")

    yield

    print("API остановлен")


app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get(
    "/",
    tags=["Статус"],
    summary="Проверка работоспособности API",
    description="Возвращает базовую информацию о сервисе.",
)
async def root() -> dict:
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
    }
