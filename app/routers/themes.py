from prisma import types
from typing import Optional
from fastapi import APIRouter, Depends, Header

from app.prisma import prisma
from app.models.auth import AccessUser
from app.utils.find_many_cursor import find_many_cursor
from app.services import auth as auth_service


router = APIRouter(
    prefix="/themes",
    tags=["themes"],
    responses={404: {"description": "Not found"}},
)


@router.get("")
async def get_themes(
    term: Optional[str] = None,
    cafeId: Optional[str] = None,
    areaB: Optional[str] = None,
    genre: Optional[str] = None,
    level: Optional[int] = None,
    person: Optional[int] = None,
    fearScore: Optional[str] = None,
    activity: Optional[str] = None,
    lockingRatio: Optional[str] = None,
    take: Optional[int] = 20,
    cursor: Optional[str] = None,
    sort: Optional[str] = "createdAt",
    order: Optional[str] = "desc",
    authorization: str = Header(default=""),
):
    current_user = None
    if authorization:
        token = authorization.replace("Bearer ", "")
        current_user = await auth_service.get_current_user(token)

    options: types.FindManyThemeArgsFromTheme = {
        "take": take + 1,
        "where": {"status": "PUBLISHED"},
        "include": {
            "cafe": True,
            "genre": True,
        },
        "order": {sort: order},
    }
    if term:
        options["where"]["name"] = {"contains": term}
    if cafeId:
        options["where"]["cafe"] = {"id": cafeId}
    if areaB:
        options["where"]["cafe"] = {"areaB": areaB}
    if genre:
        options["where"]["genre"] = {"some": {"id": genre}}
    if level:
        options["where"]["level"] = level
    if person:
        options["where"]["minPerson"] = {"lte": person}
        options["where"]["maxPerson"] = {"gte": person}
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
    if lockingRatio:
        if lockingRatio == "hight":
            options["where"]["lockingRatio"] = {"gte": 70}
        elif lockingRatio == "low":
            options["where"]["lockingRatio"] = {"gte": 1, "lte": 40}
        else:
            options["where"]["lockingRatio"] = {"gt": 40, "lt": 70}
    if cursor:
        options["cursor"] = {"id": cursor}
    if current_user:
        options["include"]["saves"] = {
            "where": {"userId": current_user.id},
        }

    themes = await prisma.theme.find_many(**options)
    result = find_many_cursor(themes, cursor=cursor)
    return result


@router.get("/{id}")
async def get_theme_detail(
    id: str,
    authorization: str = Header(default=""),
):
    current_user = None
    if authorization:
        token = authorization.replace("Bearer ", "")
        current_user = await auth_service.get_current_user(token)

    options = {
        "where": {"id": id},
        "include": {
            "cafe": True,
            "genre": True,
        },
    }
    if current_user:
        options["include"]["saves"] = {
            "where": {"userId": current_user.id},
        }

    theme = await prisma.theme.find_unique(**options)
    await prisma.theme.update(
        where={"id": id},
        data={"view": {"increment": 1}},
    )
    return theme


@router.post("/{id}/save", response_model=bool)
async def save_theme(
    id: str,
    current_user: AccessUser = Depends(auth_service.get_current_user),
):
    theme_save = await prisma.themesave.find_first(
        where={"themeId": id, "userId": current_user.id}
    )
    if not theme_save:
        await prisma.themesave.create(
            data={
                "theme": {"connect": {"id": id}},
                "user": {"connect": {"id": current_user.id}},
            }
        )
        return True
    return False


@router.post("/{id}/unsave", response_model=bool)
async def unsave_theme(
    id: str,
    current_user: AccessUser = Depends(auth_service.get_current_user),
):
    theme_save = await prisma.themesave.find_first(
        where={"themeId": id, "userId": current_user.id}
    )
    if theme_save:
        await prisma.themesave.delete(where={"id": theme_save.id})
        return True
    return False
