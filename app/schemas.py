from typing import List, Optional

from fastapi import HTTPException, status
from pydantic import BaseModel, field_validator

from app.config import settings
from app import constants


class ScrapePayloadSchema(BaseModel):
    """
        ScrapePayloadSchema model that defines the schema for the payload used in scraping operations.
        Attributes:
            page_limit (Optional[int]): The maximum number of pages to scrape. Defaults to the value of settings.DEFAULT_PAGE_LIMIT.
            proxy (Optional[str]): The proxy server to use for scraping. Defaults to an empty string.
        Methods:
            validate_page_limit(cls, value):
                Validates the page_limit attribute to ensure it is greater than or equal to 1.
                Raises:
                    HTTPException: If the page_limit is less than 1, an HTTP 400 Bad Request error is raised with a specific message.
    """
    page_limit: Optional[int] = settings.DEFAULT_PAGE_LIMIT
    proxy: Optional[str] = ''

    @field_validator('page_limit')
    def validate_page_limit(cls, value):
        if value is not None and value < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=constants.INVALID_PAGE_LIMIT_MESSAGE
            )
        
        return value


class ScrapeResponseSchema(BaseModel):
    """
        ScrapeResponseSchema model that defines the schema for the response of a scraping operation.

        Attributes:
            message (str): A message describing the result of the scraping operation.
            scraped_products_count (int):  count of the scraped products 
            created_new_products_count (int):  count of the created products in db
            updated_existing_products_count (int):  count of the updated products in db
    """
    message: str
    scraped_products_count: int
    created_new_products_count: int
    updated_existing_products_count: int