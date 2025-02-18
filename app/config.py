from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    REDIS_URL: str = "redis://localhost"
    BASE_URL: str = "https://dentalstall.com"
    DEFAULT_PROXY: str = 'shop'
    DEFAULT_PAGE_LIMIT: int = 1
    IMAGES_DIR: str = "images"
    RETRY_ATTEMPTS: int = 3
    RETRY_DELAY: int = 5  # seconds

    class Config:
        env_file = ".env"

settings = Settings()
