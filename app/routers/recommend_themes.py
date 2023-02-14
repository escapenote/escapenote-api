from prisma import models
from fastapi import APIRouter
from fastapi_cache.decorator import cache

from app.prisma import prisma


router = APIRouter(
    prefix="/recommend-themes",
    tags=["recommend-themes"],
    responses={404: {"description": "Not found"}},
)


@router.get("")
@cache(expire=86400)  # 24시간
async def get_recommend_themes():
    themes = await prisma.query_raw(
        f"""
            SELECT t.*
            FROM themes as t
            WHERE t.view >= 100
            AND t.status = 'PUBLISHED'
            ORDER BY RAND()
            LIMIT 8
        """,
        model=models.Theme,
    )

    # 테마에 소속된 카페 추가
    cafes_ids = list(map(lambda x: f"'{x.cafeId}'", themes))
    cafes_ids_str = ",".join(cafes_ids)
    cafes = await prisma.query_raw(
        f"""
        SELECT c.*
            FROM cafes as c
            WHERE c.id IN ({cafes_ids_str})
        """,
    )
    for theme in themes:
        for cafe in cafes:
            if cafe["id"] == theme.cafeId:
                theme.cafe = cafe

    # 테마에 소속된 장르 추가
    themes_ids = list(map(lambda x: f"'{x.id}'", themes))
    themes_ids_str = ",".join(themes_ids)
    genre_list = await prisma.query_raw(
        f"""
        SELECT z.*, g.*
        FROM _GenreToTheme as z
        LEFT JOIN genre as g
        ON g.id = z.A
        WHERE z.B IN ({themes_ids_str})
        """,
    )
    for theme in themes:
        theme.genre = list()
        for genre in genre_list:
            if genre["B"] == theme.id:
                theme.genre.append(genre)

    return themes
