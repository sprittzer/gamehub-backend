from typing import List

from fastapi import APIRouter, Depends, Query

from app.core.database import (
    create_game,
    delete_game,
    get_games,
    update_game,
)
from app.schemas.game import (
    GameCreate,
    GameDetailResponse,
    GameFilter,
    GameListResponse,
    GameResponse,
    GameUpdate,
)

router = APIRouter(prefix="/games", tags=["Игры"])


@router.get("", response_model=GameListResponse)
async def list_games(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    filter: GameFilter = Depends(),
):
    games, total = await get_games(page, page_size, filter)
    return GameListResponse(
        items=games,
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.get("/{game_id}", response_model=GameDetailResponse)
async def get_game_handler(game_id: int):
    return await get_game_detail(game_id)


@router.post("", response_model=GameResponse, status_code=201)
async def create_game_handler(game: GameCreate):
    return await create_game(game)


@router.patch("/{game_id}", response_model=GameResponse)
async def update_game_handler(game_id: int, game_data: GameUpdate):
    return await update_game(game_id, game_data)


@router.delete("/{game_id}", status_code=204)
async def delete_game_handler(game_id: int):
    await delete_game(game_id)
    return None


@router.get("/top", response_model=List[GameResponse])
async def get_top_games_handler(limit: int = Query(10, ge=1, le=50)):
    return await get_top_games(limit)


@router.get("/recent", response_model=List[GameResponse])
async def get_recent_games_handler(limit: int = Query(10, ge=1, le=50)):
    return await get_recent_games(limit)


@router.get("/genres", response_model=List[str])
async def get_all_genres_handler():
    return await get_all_genres()


@router.get("/platforms", response_model=List[str])
async def get_all_platforms_handler():
    return await get_all_platforms()
