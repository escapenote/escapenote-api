from fastapi import APIRouter, Depends
from app.models.cafe_reviews import UpdateCafeReview

from app.prisma import prisma
from app.models.auth import AccessUser
from app.services import auth as auth_service
from app.services import cafe_reviews as cafe_reviews_service


router = APIRouter(
    prefix="/cafe-reviews",
    tags=["cafe-reviews"],
    responses={404: {"description": "Not found"}},
)


@router.get("/{id}")
async def get_review(
    id: str,
    current_user: AccessUser = Depends(auth_service.get_current_user),
):
    """
    카페 리뷰 조회
    """
    cafereview = await prisma.cafereview.find_first(
        where={
            "id": id,
            "userId": current_user.id,
        }
    )
    return cafereview


@router.patch("/{id}")
async def update_review(
    id: str,
    cafeId: str,
    body: UpdateCafeReview,
    current_user: AccessUser = Depends(auth_service.get_current_user),
):
    """
    카페 리뷰 수정
    """
    try:
        await prisma.cafereview.update_many(
            where={
                "id": id,
                "userId": current_user.id,
            },
            data={
                "rating": body.rating,
                "text": body.text,
            },
        )

        await cafe_reviews_service.update_cafe_review(cafeId)

        return True
    except:
        return False


@router.delete("/{id}")
async def delete_review(
    id: str,
    cafeId: str,
    current_user: AccessUser = Depends(auth_service.get_current_user),
):
    """
    카페 리뷰 삭제
    """
    await prisma.cafereview.delete_many(
        where={
            "id": id,
            "userId": current_user.id,
        },
    )

    await cafe_reviews_service.update_cafe_review(cafeId)
