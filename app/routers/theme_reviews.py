from typing import Optional
from fastapi import APIRouter, Depends

from app.prisma import prisma
from app.models.auth import AccessUser
from app.models.theme_review import UpdateThemeReview
from app.utils.find_many_cursor import find_many_cursor
from app.services import auth as auth_service
from app.services import theme_reviews as theme_reviews_service


router = APIRouter(
    prefix="/theme-reviews",
    tags=["theme-reviews"],
    responses={404: {"description": "Not found"}},
)


@router.get("")
async def get_reviews(
    nickname: str,
    take: Optional[int] = 20,
    cursor: Optional[str] = None,
):
    """
    테마 리뷰 리스트 조회
    """
    options = {
        "take": take + 1,
        "where": {
            "user": {
                "nickname": nickname,
            },
        },
        "include": {
            "theme": True,
            "user": True,
        },
        "order": {"createdAt": "desc"},
    }
    if cursor:
        options["cursor"] = {"id": cursor}

    themereviews = await prisma.themereview.find_many(**options)
    result = find_many_cursor(themereviews, take=take, cursor=cursor)
    return result


@router.get("/{id}")
async def get_review(
    id: str,
    current_user: AccessUser = Depends(auth_service.get_current_user),
):
    """
    테마 리뷰 조회
    """
    themereview = await prisma.themereview.find_first(
        where={
            "id": id,
            "userId": current_user.id,
        }
    )
    return themereview


@router.patch("/{id}")
async def update_review(
    id: str,
    themeId: str,
    body: UpdateThemeReview,
    current_user: AccessUser = Depends(auth_service.get_current_user),
):
    """
    테마 리뷰 수정
    """
    try:
        await prisma.themereview.update_many(
            where={
                "id": id,
                "userId": current_user.id,
            },
            data={
                "rating": body.rating,
                "success": body.success,
                "level": body.level,
                "fear": body.fear,
                "activity": body.activity,
                "text": body.text,
            },
        )

        await theme_reviews_service.update_theme_review(themeId)

        return True
    except:
        return False


@router.delete("/{id}")
async def delete_review(
    id: str,
    themeId: str,
    current_user: AccessUser = Depends(auth_service.get_current_user),
):
    """
    테마 리뷰 삭제
    """
    await prisma.themereview.delete_many(
        where={
            "id": id,
            "userId": current_user.id,
        }
    )

    await theme_reviews_service.update_theme_review(themeId)
