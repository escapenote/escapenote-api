from fastapi import APIRouter

from app.routers import auth
from app.routers import users
from app.routers import cafes
from app.routers import recommend_cafes
from app.routers import cafe_reviews
from app.routers import genre
from app.routers import themes
from app.routers import recommend_themes
from app.routers import theme_reviews
from app.routers import sitemaps
from app.routers import faq
from app.routers import images

routers = APIRouter()

routers.include_router(auth.router)
routers.include_router(users.router)
routers.include_router(cafes.router)
routers.include_router(recommend_cafes.router)
routers.include_router(cafe_reviews.router)
routers.include_router(genre.router)
routers.include_router(themes.router)
routers.include_router(recommend_themes.router)
routers.include_router(theme_reviews.router)
routers.include_router(sitemaps.router)
routers.include_router(faq.router)
routers.include_router(images.router)
