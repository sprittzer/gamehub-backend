from typing import Dict, List

from fastapi import HTTPException
from supabase import Client, create_client

from app.core.config import settings
from app.schemas.game import GameCreate, GameUpdate

supabase: Client = create_client(
    supabase_url=settings.SUPABASE_URL,
    supabase_key=settings.SUPABASE_KEY,
)


async def get_games(page: int = 1, page_size: int = 10) -> List[Dict]:
    offset = (page - 1) * page_size
    response = (
        await supabase.table("games")
        .select("*")
        .range(offset, offset + page_size - 1)
        .execute()
    )
    return response.data


async def create_game(game_data: GameCreate) -> Dict:
    try:
        response = (
            await supabase.table("games").insert(game_data.model_dump()).execute()
        )
        return response.data[0]
    except Exception as e:
        raise HTTPException(400, f"Ошибка создания: {str(e)}")


async def get_game(game_id: int) -> Dict:
    response = (
        await supabase.table("games").select("*").eq("id", game_id).single().execute()
    )
    if not response.data:
        raise HTTPException(404, "Игра не найдена")
    return response.data


async def update_game(game_id: int, game_data: GameUpdate) -> Dict:
    data = game_data.model_dump(exclude_unset=True)
    if not data:
        raise HTTPException(400, "Нет данных для обновления")

    response = await supabase.table("games").update(data).eq("id", game_id).execute()
    if not response.data:
        raise HTTPException(404, "Игра не найдена")
    return response.data[0]


async def delete_game(game_id: int) -> bool:
    response = await supabase.table("games").delete().eq("id", game_id).execute()
    return bool(response.data)


async def update_game_average_rating(game_id: int) -> None:
    response = (
        await supabase.table("reviews")
        .select("avg(rating)", count="exact")
        .eq("game_id", game_id)
        .single()
        .execute()
    )

    if response.data and response.data.get("count", 0) > 0:
        avg_rating = round(float(response.data["avg"]), 1)
        await (
            supabase.table("games")
            .update({"average_rating": avg_rating})
            .eq("id", game_id)
            .execute()
        )
    else:
        await (
            supabase.table("games")
            .update({"average_rating": 0.0})
            .eq("id", game_id)
            .execute()
        )
