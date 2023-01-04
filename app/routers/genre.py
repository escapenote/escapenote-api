from fastapi import APIRouter
from fastapi_cache.decorator import cache

from app.prisma import prisma


router = APIRouter(
    prefix="/genre",
    tags=["genre"],
    responses={404: {"description": "Not found"}},
)

cache_options = {
    "expire": 3600,  # 1시간
    "namespace": __name__.split(".")[-1],
}


@router.get("")
@cache(expire=cache_options["expire"], namespace=cache_options["namespace"])
async def get_genreList():
    genre_list = await prisma.genre.find_many(order={"id": "asc"})
    return genre_list
