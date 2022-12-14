from typing import Optional
from fastapi import APIRouter

from app.prisma import prisma
from app.utils.find_many_cursor import find_many_cursor


router = APIRouter(
    prefix="/themes",
    tags=["themes"],
    responses={404: {"description": "Not found"}},
)


@router.get("")
async def get_themes(
    genre: Optional[str] = None,
    areaB: Optional[str] = None,
    level: Optional[float] = None,
    take: Optional[int] = 20,
    cursor: Optional[str] = None,
):
    options = {
        "take": take + 1,
        "where": {"status": "PUBLISHED"},
        "include": {
            "cafe": True,
            "genre": True,
        },
        "order": {"createdAt": "desc"},
    }
    if genre:
        options["where"]["genre"] = {"id": genre}
    if areaB:
        options["where"]["cafe"] = {"areaB": areaB}
    if level:
        options["where"]["level"] = level
    if cursor:
        options["cursor"] = {"id": cursor}

    themes = await prisma.theme.find_many(**options)
    result = find_many_cursor(themes, cursor=cursor)
    return result


@router.get("/{id}")
async def get_theme_detail(id: str):
    theme = await prisma.theme.find_unique(
        where={"id": id},
        include={"genre": True},
    )
    return theme
