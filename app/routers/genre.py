from fastapi import APIRouter

from app.prisma import prisma


router = APIRouter(
    prefix="/genre",
    tags=["genre"],
    responses={404: {"description": "Not found"}},
)


@router.get("")
async def get_genreList():
    genre_list = await prisma.genre.find_many(order={"id": "asc"})
    return genre_list
