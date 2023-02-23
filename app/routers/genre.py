from prisma import types
from typing import Optional
from fastapi import APIRouter
from fastapi_cache.decorator import cache

from app.prisma import prisma


router = APIRouter(
    prefix="/genre",
    tags=["genre"],
    responses={404: {"description": "Not found"}},
)


@router.get("")
@cache(expire=3600)  # 1시간
async def get_genreList(term: Optional[str] = None):
    options: types.FindManyGenreArgsFromGenre = {
        "where": {},
        "include": {"themes": True},
        "order": {"id": "asc"},
    }
    if term:
        options["where"]["id"] = {"contains": term}

    genre_list = await prisma.genre.find_many(**options)
    return genre_list
