from prisma import types
from typing import Optional
from fastapi import APIRouter, Depends, Header

from app.prisma import prisma
from app.models.auth import AccessUser
from app.utils.find_many_cursor import find_many_cursor
from app.services import auth as auth_service


router = APIRouter(
    prefix="/cafes",
    tags=["cafes"],
    responses={404: {"description": "Not found"}},
)


@router.get("")
async def get_cafes(
    term: Optional[str] = None,
    areaB: Optional[str] = None,
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

    options: types.FindManyCafeArgsFromCafe = {
        "take": take + 1,
        "where": {"status": "PUBLISHED"},
        "include": {"themes": True},
        "order": {sort: order},
    }
    if term:
        options["where"]["name"] = {"contains": term}
    if areaB:
        options["where"]["areaB"] = areaB
    if cursor:
        options["cursor"] = {"id": cursor}
    if current_user:
        options["include"]["saves"] = {
            "where": {"userId": current_user.id},
        }

    cafes = await prisma.cafe.find_many(**options)
    result = find_many_cursor(cafes, cursor=cursor)
    return result


@router.get("/{id}")
async def get_cafe_detail(
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
            "themes": {
                "include": {
                    "genre": True,
                },
            },
        },
    }
    if current_user:
        options["include"]["saves"] = {
            "where": {"userId": current_user.id},
        }

    cafe = await prisma.cafe.find_unique(**options)
    await prisma.cafe.update(
        where={"id": id},
        data={"view": {"increment": 1}},
    )
    return cafe


@router.post("/{id}/save", response_model=bool)
async def save_cafe(
    id: str,
    current_user: AccessUser = Depends(auth_service.get_current_user),
):
    cafe_save = await prisma.cafesave.find_first(
        where={"cafeId": id, "userId": current_user.id}
    )
    if not cafe_save:
        await prisma.cafesave.create(
            data={
                "cafe": {"connect": {"id": id}},
                "user": {"connect": {"id": current_user.id}},
            }
        )
        return True
    return False


@router.post("/{id}/unsave", response_model=bool)
async def unsave_cafe(
    id: str,
    current_user: AccessUser = Depends(auth_service.get_current_user),
):
    cafe_save = await prisma.cafesave.find_first(
        where={"cafeId": id, "userId": current_user.id}
    )
    if cafe_save:
        await prisma.cafesave.delete(where={"id": cafe_save.id})
        return True
    return False
