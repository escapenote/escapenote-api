from typing import Optional
from fastapi import APIRouter, Depends

from app.prisma import prisma
from app.models.user import User
from app.services import auth as auth_service
from app.utils.find_many_cursor import find_many_cursor


router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@router.get("", response_model=User)
async def get_user(nickname: str):
    user = await prisma.user.find_unique(
        where={
            "nickname": nickname,
        },
        include={
            "cafeReviews": True,
            "themeReviews": True,
        },
    )
    return user


@router.get("/saved_cafes")
async def get_saved_cafes(
    current_user: User = Depends(auth_service.get_current_user),
    take: Optional[int] = 20,
    cursor: Optional[str] = None,
):
    options = {
        "take": take + 1,
        "where": {
            "saves": {"some": {"userId": current_user.id}},
        },
        "include": {
            "saves": True,
        },
    }
    if cursor:
        options["cursor"] = {"id": cursor}

    cafes = await prisma.cafe.find_many(**options)
    result = find_many_cursor(cafes, cursor=cursor)
    return result


@router.get("/saved_themes")
async def get_saved_themes(
    current_user: User = Depends(auth_service.get_current_user),
    take: Optional[int] = 20,
    cursor: Optional[str] = None,
):
    options = {
        "take": take + 1,
        "where": {
            "saves": {"some": {"userId": current_user.id}},
        },
        "include": {
            "saves": True,
            "cafe": True,
            "genre": True,
        },
    }
    if cursor:
        options["cursor"] = {"id": cursor}

    themes = await prisma.theme.find_many(**options)
    result = find_many_cursor(themes, cursor=cursor)
    return result
