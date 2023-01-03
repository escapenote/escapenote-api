from typing import Optional
from fastapi import APIRouter
from prisma import types

from app.prisma import prisma
from app.utils.find_many_cursor import find_many_cursor


router = APIRouter(
    prefix="/themes",
    tags=["themes"],
    responses={404: {"description": "Not found"}},
)


@router.get("")
async def get_themes(
    term: Optional[str] = None,
    areaB: Optional[str] = None,
    genre: Optional[str] = None,
    level: Optional[int] = None,
    person: Optional[int] = None,
    minPrice: Optional[int] = None,
    maxPrice: Optional[int] = None,
    fearScore: Optional[str] = None,
    activity: Optional[str] = None,
    minLockingRatio: Optional[int] = None,
    maxLockingRatio: Optional[int] = None,
    take: Optional[int] = 20,
    cursor: Optional[str] = None,
):
    options: types.FindManyThemeArgsFromTheme = {
        "take": take + 1,
        "where": {"status": "PUBLISHED"},
        "include": {
            "cafe": True,
            "genre": True,
        },
        "order": {"createdAt": "desc"},
    }
    if term:
        options["where"]["name"] = {"contains": term}
    if areaB:
        options["where"]["cafe"] = {"areaB": areaB}
    if genre:
        options["where"]["genre"] = {"some": {"id": genre}}
    if level:
        options["where"]["level"] = level
    if person:
        options["where"]["minPerson"] = {"lte": person}
        options["where"]["maxPerson"] = {"gte": person}
    if minPrice or maxPrice:
        if minPrice and maxPrice:
            options["where"]["price"] = {"gte": minPrice, "lte": maxPrice}
        elif minPrice:
            options["where"]["price"] = {"gte": minPrice}
        elif maxPrice:
            options["where"]["price"] = {"lte": maxPrice}
    if fearScore:
        if fearScore == "hight":
            options["where"]["fear"] = {"gte": 4}
        elif fearScore == "low":
            options["where"]["fear"] = {"gte": 1, "lte": 2}
        else:
            options["where"]["fear"] = {"gt": 2, "lt": 4}
    if activity:
        if activity == "hight":
            options["where"]["activity"] = {"gte": 4}
        elif activity == "low":
            options["where"]["activity"] = {"gte": 1, "lte": 2}
        else:
            options["where"]["activity"] = {"gt": 2, "lt": 4}
    if minLockingRatio or maxLockingRatio:
        if minLockingRatio and maxLockingRatio:
            options["where"]["lockingRatio"] = {
                "gte": minLockingRatio,
                "lte": maxLockingRatio,
            }
        elif minLockingRatio:
            options["where"]["lockingRatio"] = {"gte": minLockingRatio}
        elif maxLockingRatio:
            options["where"]["lockingRatio"] = {"lte": maxLockingRatio}
    if cursor:
        options["cursor"] = {"id": cursor}

    await prisma.theme.find_many(where={"genre": {"every": {}}})

    themes = await prisma.theme.find_many(**options)
    result = find_many_cursor(themes, cursor=cursor)
    return result


@router.get("/{id}")
async def get_theme_detail(id: str):
    theme = await prisma.theme.find_unique(
        where={"id": id},
        include={
            "cafe": True,
            "genre": True,
        },
    )
    return theme
