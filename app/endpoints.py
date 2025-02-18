from fastapi import APIRouter, Depends, Request, status

from app.authentication import verify_token
from app.libs.cache.redis_cache import cache_client
from app import constants
from app.libs.notification.console_notifier import ConsoleNotifier
from app.schemas import ScrapePayloadSchema, ScrapeResponseSchema
from app.libs.scraper.scraper import DentalScraper
from app.libs.storage.json_storage import JsonStorage

router = APIRouter()


# 1.) currently providing support for proxy as a single string only.
# 2.) Could be handled in a better way using different body params such as filters, url etc
#     but keeping it this way itself as per the documentation provided.
@router.post(
    constants.SCRAPE_PRODUCTS,
    status_code=status.HTTP_201_CREATED,
    response_model=ScrapeResponseSchema
)
async def scrape_products(
    request: Request,
    payload: ScrapePayloadSchema,
    _=Depends(verify_token)
):
    """
        Endpoint to scrape products from a dental products website.
        Args:
            request (Request): The HTTP request object.
            payload (ScrapePayloadSchema): The payload containing scraping parameters.
            _ (Depends): Dependency to verify the token.
        Returns:
            dict: A dictionary containing a message and the count of scraped products.
        Raises:
            HTTPException: If an error occurs during scraping.
    """
    # Initialize components
    scraper = DentalScraper(payload.proxy)
    storage = JsonStorage(file_path=constants.PRODUCTS_OBJECT_PATH)
    notifier = ConsoleNotifier()
    # Scrape products
    products = scraper.scrape_products(payload.page_limit)
    # Convert to storage format and check cache
    updated_products = []
    updated_count = 0
    
    # get cache values of products
    cache_price = cache_client.mget(
        keys=[constants.REDIS_PRODUCT_PROCE_KEY.format(product_id=product['title']) for product in products]
    )
    cache_data = {}
    for price, product in zip(cache_price, products):
        # No db fallback is checked for the price in file system based db as of now
        # hence if cache expires we set the data again for all scraped products.
        if price != product['price']:
            updated_count += 1
            cache_data[constants.REDIS_PRODUCT_PROCE_KEY.format(product_id=product['title'])] = product['price']
            updated_products.append({
                "product_title": product['title'],
                "product_price": product['price'],
                "path_to_image": product['image_path']
            })
            
    if cache_data:
        cache_client.mset(cache_data)

    # Save to storage (it handles the creation and updation part internally)
    created_objects = storage.save_object(updated_products)
    # Notify about completion
    notifier.notify_scraping_complete(len(products), updated_count)

    return {
        "message": constants.SCRAPING_COMPLETE,
        "scraped_products_count": len(products),
        "created_new_products_count": len(created_objects),
        "updated_existing_products_count": updated_count - len(created_objects)
    }
