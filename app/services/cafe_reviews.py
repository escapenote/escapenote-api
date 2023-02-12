from app.prisma import prisma


async def update_cafe_review(cafeId: str):
    """
    카페 리뷰들을 읽어와 평점을 계산하여 카페에 평균 데이터를 업데이트 한다.
    """
    reviews = await prisma.cafereview.find_many(where={"cafeId": cafeId})
    reviews_count = len(reviews)
    if reviews_count:
        reviews_rating = sum(list(map(lambda x: x.rating, reviews))) / reviews_count
    else:
        reviews_rating = 0

    await prisma.cafe.update(
        where={"id": cafeId},
        data={
            "reviewsRating": reviews_rating,
            "reviewsCount": reviews_count,
        },
    )
