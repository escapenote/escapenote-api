from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend

from app.prisma import prisma
from app.config import settings
from app.routers import routers

if settings.app_env == "production":
    app = FastAPI(
        docs_url=None,
        redoc_url=None,
        default_response_class=ORJSONResponse,
    )
else:
    app = FastAPI(
        title="Escapenote API",
        version="1.0.0",
        default_response_class=ORJSONResponse,
    )

# CORS Origins
origins = [
    "http://localhost:3000",
    "https://escape-note.com",
    "https://www.escape-note.com",
]

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Init Fastapi Cache
@app.on_event("startup")
async def startup():
    FastAPICache.init(InMemoryBackend(), prefix="escapenote-api-cache")


# Flush Fastapi Cache
@app.get("/cache/flush/{namespace}", tags=["CACHE"])
async def clear_caches(namespace: str):
    return {
        "namespace": namespace,
        "status": await FastAPICache.clear(namespace=namespace),
    }


# Prisma startup
@app.on_event("startup")
async def startup():
    await prisma.connect()


# Prisma shutdown
@app.on_event("shutdown")
async def shutdown():
    await prisma.disconnect()


@app.get("/")
def root():
    return {
        "name": "Escapenote",
        "version": "1.0.0",
    }


# Routers
app.include_router(routers)
