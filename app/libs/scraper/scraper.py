import os
import time
import requests

from bs4 import BeautifulSoup, Tag
from typing import Optional, List

from app.config import settings
from app import constants
from app.utils import parse_proxy


class DentalScraper:
    def __init__(self, proxy: Optional[str]):
        self.base_url = settings.BASE_URL
        self.proxy = proxy or settings.DEFAULT_PROXY
        self.session = requests.Session()

    def _get_with_retry(self, url: str) -> requests.Response:
        """
            Attempts to perform a GET request to the specified URL with retries.
            Args:
                url (str): The URL to send the GET request to.
            Returns:
                requests.Response: The response object resulting from the GET request.
            Raises:
                requests.RequestException: If the request fails after the specified number of retry attempts.
        """
        for attempt in range(settings.RETRY_ATTEMPTS):
            try:
                response = self.session.get(url)
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                if attempt == settings.RETRY_ATTEMPTS - 1:
                    raise e
                time.sleep(settings.RETRY_DELAY)

    def _download_image(self, url: str) -> str:
        """
            Downloads an image from the given URL and saves it to the specified directory.
            Args:
                url (str): The URL of the image to download.
            Returns:
                str: The file path where the image is saved.
            Raises:
                requests.exceptions.RequestException: If there is an issue with the HTTP request.
        """
        response = self._get_with_retry(url)
        filename = url.split('/')[-1]
        path = os.path.join(settings.IMAGES_DIR, filename)
        
        os.makedirs(settings.IMAGES_DIR, exist_ok=True)
        with open(path, 'wb') as f:
            f.write(response.content)
        
        return path
        
    def _extract_price(self, price_text: str) -> float:
        """
            Extracts and converts a price from a string to a float.

            This method removes the currency symbol (₹), commas, and any surrounding whitespace
            from the input price string and converts the cleaned string to a float. If the input
            string is not a valid number, it catches the exception and returns 0.0.

            Args:
                price_text (str): The price string to be cleaned and converted.

            Returns:
                float: The extracted price as a float. Returns 0.0 if the input string is invalid.
        """
        try:
            cleaned_price = price_text.replace('₹', '').replace(',', '').strip()
            return float(cleaned_price)
        except (ValueError, AttributeError) as e:
            print(constants.EXTRACT_PRICE_ERROR.format(price_text=price_text, error=str(e)))
            return 0.0

    def _extract_title_from_html(self, title_elem: Tag) -> str:
        """
            Extracts and formats the product title from an HTML element.
            This method takes an HTML element containing a product URL, extracts the 
            product title from the URL, and converts it into a readable format. If the 
            extraction fails, it falls back to using the text content of the HTML element.
            Args:
                title_elem (Tag): The HTML element containing the product URL.
            Returns:
                str: The formatted product title.
        """
        product_url = title_elem.get('href', '')
        title = ''
        try:
            # Extract the part between 'product/' and the last '/'
            title = product_url.split('product/')[-1].strip('/')
            # Convert URL format to readable title
            title = ' '.join(word.capitalize() for word in title.split('-'))
        except Exception as e:
            print(constants.EXTRACT_TITLE_FROM_HTML_ERROR.format(product_url=product_url, error=str(e)))
            title = title_elem.text.strip()
        
        return title

    def _extract_detail_page(self, soup: BeautifulSoup) -> Optional[dict]:
        """
            Extracts product details from a BeautifulSoup object representing a product detail page.
            Args:
                soup (BeautifulSoup): A BeautifulSoup object containing the HTML of the product detail page.
            Returns:
                Optional[Product]: A Product object containing the extracted details (title, price, image URL) if all required elements are found,
                                otherwise None.
            The method performs the following steps:
            1. Extracts the product title from an <h1> element with the class 'product_title'.
            2. Extracts the product price from a <p> element with the class 'price', first trying to get the sale price, then the regular price.
            3. Extracts the product image URL from an <img> element within a <div> with the class 'woocommerce-product-gallery__image'.
            4. If any of the required elements (title, price, image) are missing, logs the missing elements and returns None.
            5. If all required elements are found, creates a Product object with the extracted details and downloads the product image.
            Raises:
                Exception: If an error occurs during the extraction process, logs the error and returns None.
        """
        try:
            # Get title element
            title_elem = soup.select_one('h1.product_title')
            
            # Try to get sale price first, then regular price
            price_elem = soup.select_one('p.price ins span.woocommerce-Price-amount bdi')
            if not price_elem:
                price_elem = soup.select_one('p.price span.woocommerce-Price-amount bdi')
            
            # Get product image with multiple fallbacks
            # Get product image
            img_elem = soup.select_one('div.woocommerce-product-gallery__image img.wp-post-image')
            if not img_elem:
                # Try fallback selector without wp-post-image class
                img_elem = soup.select_one('div.woocommerce-product-gallery__image img')

            if img_elem:
                image_url = img_elem.get('src')

            if not all([title_elem, price_elem, img_elem]):
                missing = []
                if not title_elem: missing.append('title')
                if not price_elem: missing.append('price')
                if not img_elem: missing.append('image')
                print(constants.MISSING_ELEMENTS_ERROR.format(missing=', '.join(missing)))
                return None

            title = title_elem.text.strip()
            price = self._extract_price(price_elem.text.strip())
            image_url = img_elem.get('src')

            product = {
                'title': title, 'price': price, 'image_url': image_url,
                'image_path': self._download_image(image_url)
            }
            return product
        except Exception as e:
            print(constants.ERROR_EXTRACTING_PRODUCT_DETAILS.format(error=str(e)))
            return None

    def _scrape_product_detail_page_info(self, base_url: str, query: str, products: List) -> bool:
        """
            Scrapes product detail page information and appends it to the products list if the page is a valid product detail page.
            Args:
                base_url (str): The base URL of the website.
                query (str): The query string to append to the base URL.
                products (list): The list to which the scraped product details will be appended.
            Returns:
                bool: True if the page is a product detail page and product details were successfully scraped and appended to the products list, False otherwise.
            Raises:
                Exception: If there is an error while checking the page type.
        """
        # Check if this is a product detail page
        url = f"{self.base_url}/{base_url}/{query or ''}"
        try:
            response = self._get_with_retry(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # If we find a product title heading, this is a detail page
            if soup.select_one('h1.product_title'):
                product = self._extract_detail_page(soup)
                if product:
                    products.append(product)
                return True

        except Exception as e:
            print(constants.ERROR_CHECKING_PAGE_TYPE.format(str(e)))
            return False
        
        return False

    def scrape_products(self, page_limit: Optional[int] = settings.DEFAULT_PAGE_LIMIT) -> List[dict]:
        """
            Scrapes products from the website up to a specified page limit.
            Args:
                page_limit (Optional[int]): The maximum number of pages to scrape. Defaults to settings.DEFAULT_PAGE_LIMIT.
            Returns:
                List[Product]: A list of Product objects containing the scraped product details.
            The method performs the following steps:
            1. Parses the proxy to get the base URL, page number, and query.
            2. Checks if the current page is a product detail page. If so, it scrapes the product details and returns.
            3. If not a detail page, it proceeds with category page scraping.
            4. Iterates through the pages up to the specified page limit, scraping product details from each page.
            5. For each product element found, it extracts the title, price, and image URL.
            6. Handles lazy-loaded images and downloads the product image.
            7. Appends the scraped product details to the products list.
            8. Handles exceptions and continues scraping the next product or page if an error occurs.
            Raises:
                Exception: If an error occurs during the scraping process, it prints the error message and stops scraping further pages.
        """

        products = []
        base_url, page_number, query = parse_proxy(self.proxy)
        current_page = page_number or 1
        max_limit = current_page + page_limit
        
        # check if its a product detail page -> If so just return the products response with that particular product
        is_detail_page = self._scrape_product_detail_page_info(
            base_url=base_url, query=query, products=products
        )

        # If not a detail page, proceed with category page scraping
        while current_page < max_limit and not is_detail_page:
            url = f"{self.base_url}/{base_url}/page/{current_page}/{query or ''}"
            try:
                response = self._get_with_retry(url)
                soup = BeautifulSoup(response.content, 'html.parser')
                product_elements = soup.select('li.product')
                if not product_elements:
                    break

                for element in product_elements:
                    try:
                        title_elem = element.select_one('h2.woo-loop-product__title a')
                        price_box = element.select_one('.mf-product-price-box')
                        price_elem = price_box.select_one('.woocommerce-Price-amount bdi') if price_box else None
                        img_elem = element.select_one('.mf-product-thumbnail img')

                        # check if all elements are avlb for scraping
                        if not all([title_elem, price_elem, img_elem]):
                            missing = []
                            if not title_elem: missing.append('title')
                            if not price_elem: missing.append('price')
                            if not img_elem: missing.append('image')
                            print(constants.MISSING_ELEMENTS_ERROR.format(', '.join(missing)))
                            return None
                        
                        title = self._extract_title_from_html(title_elem)
                        price = self._extract_price(price_elem.text.strip())
                        # Handle lazy-loaded images
                        image_url = img_elem.get('data-lazy-src') or img_elem.get('src', '')
                        
                        product = {
                            'title': title, 'price': price, 'image_url': image_url,
                            'image_path': self._download_image(image_url)
                        }
                        products.append(product)
                    except Exception as e:
                        print(constants.ERROR_PROCESSING_PRODUCT_ELEMENT.format(error=str(e)))
                        continue

                current_page += 1
            except Exception as e:
                print(constants.ERROR_SCRAPING_PAGE.format(current_page=current_page, error=str(e)))
                break

        return products
