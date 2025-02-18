# Error/Validation message's
INVALID_PAGE_LIMIT_MESSAGE = "Page limit must be a positive integer"
API_KEY_NOT_FOUND = 'No API token found in DB'
MISSING_TOKEN_IN_HEADERS = 'Auth token not found in headers'
INVALID_TOKEN = 'Invalid Auth token'

# Scraper related errors
EXTRACT_PRICE_ERROR = 'Error extracting price from "{price_text}": "{error}"'
EXTRACT_TITLE_FROM_HTML_ERROR = 'Failed to extract title from URL {product_url}: {error}'
MISSING_ELEMENTS_ERROR = "Missing required elements on detail page: {missing}"
ERROR_EXTRACTING_PRODUCT_DETAILS = 'Error extracting product details: {error}'
ERROR_CHECKING_PAGE_TYPE = 'Error checking page type: {error}'
ERROR_PROCESSING_PRODUCT_ELEMENT = 'Error processing product element: {error}'
ERROR_SCRAPING_PAGE = 'Error scraping page {current_page}: {error}'

# Success Messages
SCRAPING_COMPLETE = 'Scraping completed successfully'

# storage constants
BASE_DIR = 'db_objects'
API_TOKEN_PATH = BASE_DIR + '/secret_token.json'
PRODUCTS_OBJECT_PATH = BASE_DIR + '/products.json'

# API Endpoint constants
SCRAPE_PRODUCTS = '/scrape/'

# Cache keys
REDIS_PRODUCT_PROCE_KEY = 'product:{product_id}:price'

# Notifier constants
SUCCESS_NOTIFIER_MESSAGE = 'Scraping completed! Scraped {products_count} products, updated {updated_count} products'
