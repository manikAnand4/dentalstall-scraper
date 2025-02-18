import redis

from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI

from app import endpoints
from app.config import settings
from app.libs import cache


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize cache
    try:
        cache.REDIS_CLIENT = redis.from_url(settings.REDIS_URL)
        yield
    finally:
    # Close cache
        if cache.REDIS_CLIENT:
            cache.REDIS_CLIENT.close()


# setup router config
router = APIRouter(prefix='/v1')
router.include_router(endpoints.router, prefix='')

app = FastAPI(lifespan=lifespan)
app.include_router(router)
