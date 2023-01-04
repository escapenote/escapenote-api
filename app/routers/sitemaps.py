from fastapi import APIRouter
from fastapi_cache.decorator import cache

from app.prisma import prisma


router = APIRouter(
    prefix="/sitemaps",
    tags=["sitemaps"],
    responses={404: {"description": "Not found"}},
)

cache_options = {
    "expire": 86400,  # 24시간
    "namespace": __name__.split(".")[-1],
}


@router.get("/cafes")
@cache(expire=cache_options["expire"], namespace=cache_options["namespace"])
async def get_cafes():
    cafes = await prisma.cafe.find_many(
        where={"status": "PUBLISHED"},
        order={"createdAt": "desc"},
    )
    cafes = list(
        map(
            lambda x: {
                "id": x.id,
                "updatedAt": x.updatedAt,
            },
            cafes,
        )
    )
    return cafes


@router.get("/themes")
@cache(expire=cache_options["expire"], namespace=cache_options["namespace"])
async def get_themes():
    themes = await prisma.theme.find_many(
        where={"status": "PUBLISHED"},
        order={"createdAt": "desc"},
    )
    themes = list(
        map(
            lambda x: {
                "id": x.id,
                "updatedAt": x.updatedAt,
            },
            themes,
        )
    )
    return themes
