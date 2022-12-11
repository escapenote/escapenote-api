from typing import Optional
from fastapi import APIRouter

from app.prisma import prisma
from app.utils.find_many_cursor import find_many_cursor


router = APIRouter(
    prefix="/cafes",
    tags=["cafes"],
    responses={404: {"description": "Not found"}},
)


@router.get("")
async def get_cafes(
    areaB: Optional[str] = None,
    take: Optional[int] = 20,
    cursor: Optional[str] = None,
):
    options = {
        "take": take + 1,
        "where": {"status": "PUBLISHED"},
        "include": {
            "themes": True
        },
        "order": {"createdAt": "desc"},
    }
    if areaB:
        options["where"]["areaB"] = areaB
    if cursor:
        options["cursor"] = {"id": cursor}

    cafes = await prisma.cafe.find_many(**options)
    result = find_many_cursor(cafes, cursor=cursor)
    return result


@router.get("/{id}")
async def get_cafe_detail(id: str):
    cafe = await prisma.cafe.find_unique(
        where={"id": id},
    )
    return cafe
