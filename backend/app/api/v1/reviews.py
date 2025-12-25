from typing import List

from fastapi import APIRouter, HTTPException, Query, Request

from app.core.database import supabase, update_game_average_rating
from app.schemas.review import (
    ReviewCreate,
    ReviewListResponse,
    ReviewUpdate,
)

router = APIRouter(prefix="/reviews", tags=["Рецензии"])


@router.get("", response_model=ReviewListResponse)
async def get_all_reviews(
    page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100)
):
    offset = (page - 1) * page_size
    response = (
        supabase.table("reviews")
        .select("*")
        .range(offset, offset + page_size - 1)
        .execute()
    )

    return ReviewListResponse(
        items=response.data,
        total=len(response.data),
        page=page,
        page_size=page_size,
        pages=1,
    )


@router.get("/recent", response_model=List[dict])
async def get_recent_reviews(limit: int = Query(10, ge=1, le=50)):
    response = (
        supabase.table("reviews")
        .select("*, game(*)")
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return response.data


@router.get("/{review_id}", response_model=dict)
async def get_review(review_id: int):
    response = (
        supabase.table("reviews")
        .select("*, game(*)")
        .eq("id", review_id)
        .single()
        .execute()
    )
    if not response.data:
        raise HTTPException(status_code=404, detail="Рецензия не найдена")
    return response.data


@router.post("", response_model=dict, status_code=201)
async def create_review(review: ReviewCreate, request: Request):
    ip = request.client.host

    game_check = supabase.table("games").select("id").eq("id", review.game_id).execute()
    if not game_check.data:
        raise HTTPException(404, "Игра не найдена")

    duplicate = (
        supabase.table("reviews")
        .select("id")
        .eq("game_id", review.game_id)
        .eq("ip_address", ip)
        .execute()
    )
    if duplicate.data:
        raise HTTPException(409, "У вас уже есть рецензия на эту игру")

    review_data = review.dict()
    review_data["ip_address"] = ip
    response = supabase.table("reviews").insert(review_data).execute()

    await update_game_average_rating(review.game_id)

    return response.data[0]


@router.patch("/{review_id}", response_model=dict)
async def update_review(review_id: int, update_data: ReviewUpdate, request: Request):
    review = (
        supabase.table("reviews").select("*").eq("id", review_id).single().execute()
    )
    if not review.data:
        raise HTTPException(status_code=404, detail="Рецензия не найдена")

    review_data = review.data
    if review_data["ip_address"] != request.client.host:
        raise HTTPException(403, "Нет доступа")

    update_dict = update_data.dict(exclude_unset=True)
    response = (
        supabase.table("reviews").update(update_dict).eq("id", review_id).execute()
    )

    await update_game_average_rating(review_data["game_id"])

    return response.data[0]


@router.delete("/{review_id}", status_code=204)
async def delete_review(review_id: int, request: Request):
    review = (
        supabase.table("reviews").select("*").eq("id", review_id).single().execute()
    )
    if not review.data:
        raise HTTPException(status_code=404, detail="Рецензия не найдена")

    if review.data["ip_address"] != request.client.host:
        raise HTTPException(403, "Нет доступа")

    supabase.table("reviews").delete().eq("id", review_id).execute()
    await update_game_average_rating(review.data["game_id"])

    return None


@router.get("/game/{game_id}", response_model=dict)
async def get_game_reviews(game_id: int):
    game = supabase.table("games").select("*").eq("id", game_id).single().execute()
    if not game.data:
        raise HTTPException(status_code=404, detail="Игра не найдена")

    reviews = (
        supabase.table("reviews").select("*, game(*)").eq("game_id", game_id).execute()
    )

    return {
        "game_id": game_id,
        "game_title": game.data["title"],
        "average_rating": game.data["average_rating"],
        "reviews_count": len(reviews.data),
        "items": reviews.data,
    }
