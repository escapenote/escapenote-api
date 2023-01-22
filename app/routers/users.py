from fastapi import APIRouter

from app.prisma import prisma


router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@router.get("/{nickname}")
async def get_user(nickname: str):
    user = await prisma.user.find_unique(where={"nickname": nickname})
    return user
