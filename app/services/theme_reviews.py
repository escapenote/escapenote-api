from app.prisma import prisma


async def update_theme_review(themeId: str):
    """
    테마 리뷰들을 읽어와 평점을 계산하여 테마에 평균 데이터를 업데이트 한다.
    """
    reviews = await prisma.themereview.find_many(where={"themeId": themeId})
    reviews_count = len(reviews)

    reviews_rating_score = 0
    reviews_level_score = 0
    reviews_level_count = 0
    reviews_fear_score = 0
    reviews_fear_count = 0
    reviews_activity_score = 0
    reviews_activity_count = 0
    for review in reviews:
        reviews_rating_score += review.rating
        if review.level:
            reviews_level_score += review.level
            reviews_level_count += 1
        if review.fear:
            reviews_fear_score += review.fear
            reviews_fear_count += 1
        if review.activity:
            reviews_activity_score += review.activity
            reviews_activity_count += 1

    reviews_rating = reviews_rating_score / reviews_count if reviews_count else 0
    reviews_level = (
        reviews_level_score / reviews_level_count if reviews_level_count else 0
    )
    reviews_fear = reviews_fear_score / reviews_fear_count if reviews_fear_count else 0
    reviews_activity = (
        reviews_activity_score / reviews_activity_count if reviews_activity_count else 0
    )

    await prisma.theme.update(
        where={"id": themeId},
        data={
            "reviewsRating": reviews_rating,
            "reviewsLevel": reviews_level,
            "reviewsFear": reviews_fear,
            "reviewsActivity": reviews_activity,
            "reviewsCount": reviews_count,
        },
    )
