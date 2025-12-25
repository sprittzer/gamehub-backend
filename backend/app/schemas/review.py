from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ReviewBase(BaseModel):
    rating: int = Field(
        ...,
        ge=1,
        le=10,
        description="Оценка игры от 1 до 10",
        examples=[8],
    )
    text: str = Field(
        ...,
        min_length=10,
        description="Текст рецензии",
        examples=["The Witcher 3 — это шедевр!!!"],
    )


class ReviewCreate(ReviewBase):
    game_id: int = Field(
        ...,
        description="ID игры, на которую пишется рецензия",
        examples=[1],
    )


class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(
        None,
        ge=1,
        le=10,
        description="Новая оценка игры",
    )
    text: Optional[str] = Field(
        None,
        min_length=10,
        description="Новый текст рецензии",
    )


class ReviewGame(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="ID игры")
    title: str = Field(..., description="Название игры")


class ReviewResponse(ReviewBase):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="ID рецензии")
    game_id: int = Field(..., description="ID игры")
    ip_address: str = Field(..., description="IP автора")
    created_at: datetime = Field(..., description="Дата создания")


class ReviewDetailResponse(ReviewBase):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="ID рецензии")
    game: ReviewGame = Field(..., description="Игра")
    ip_address: str = Field(..., description="IP автора")
    created_at: datetime = Field(..., description="Дата создания")


class ReviewListResponse(BaseModel):
    items: List[ReviewResponse] = Field(..., description="Список рецензий")
    total: int = Field(..., description="Всего рецензий")
    page: int = Field(..., ge=1, description="Страница")
    page_size: int = Field(..., ge=1, description="Размер страницы")
    pages: int = Field(..., ge=0, description="Страниц всего")


class GameReviewsResponse(BaseModel):
    game_id: int = Field(..., description="ID игры")
    game_title: str = Field(..., description="Название игры")
    average_rating: float = Field(..., ge=0, le=10, description="Средний рейтинг игры")
    reviews_count: int = Field(..., description="Количество рецензий")
    items: List[ReviewDetailResponse] = Field(..., description="Список рецензий")
