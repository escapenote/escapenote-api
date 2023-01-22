from fastapi import APIRouter

from app.routers import auth
from app.routers import users
from app.routers import cafes
from app.routers import genre
from app.routers import themes
from app.routers import sitemaps

routers = APIRouter()

routers.include_router(auth.router)
routers.include_router(users.router)
routers.include_router(cafes.router)
routers.include_router(genre.router)
routers.include_router(themes.router)
routers.include_router(sitemaps.router)
