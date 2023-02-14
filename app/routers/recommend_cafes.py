from fastapi import APIRouter
from fastapi_cache.decorator import cache

from app.prisma import prisma

router = APIRouter(
    prefix="/recommend-cafes",
    tags=["recommend-cafes"],
    responses={404: {"description": "Not found"}},
)


@router.get("")
@cache(expire=86400)  # 24시간
async def get_recommend_cafes():
    cafes = await prisma.query_raw(
        f"""
            SELECT c.*
            FROM cafes as c
            WHERE c.view >= 100
            AND c.status = 'PUBLISHED'
            ORDER BY RAND()
            LIMIT 8
        """,
    )

    return cafes
