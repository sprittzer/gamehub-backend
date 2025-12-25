from fastapi import APIRouter

from app.api.v1.games import router as games_router
from app.api.v1.reviews import router as reviews_router

api_router = APIRouter()

api_router.include_router(games_router)
api_router.include_router(reviews_router)
