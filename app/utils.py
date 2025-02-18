import re
from typing import Optional, Tuple

def parse_proxy(url: Optional[str]) -> Tuple[Optional[str], Optional[int], Optional[str]]:
    """Parse a URL string to extract base URL, page number, and query parameters.
    
    Args:
        url: A URL string to parse. Can be None or empty.
    
    Returns:
        A tuple of (base_url, page_number, query_params), where:
            - base_url: The base path without page number or query params
            - page_number: Page number if found, else None
            - query_params: Query string starting with '?' if found, else None
    
    Examples:
        >>> parse_url('shop/page/2/?min_price=43831&max_price=675000')
        ('shop', 2, '?min_price=43831&max_price=675000')
        
        >>> parse_url('shop/?min_price=43831&max_price=675000')
        ('shop', None, '?min_price=43831&max_price=675000')
        
        >>> parse_url('product-brand/gdc/')
        ('product-brand/gdc', None, None)
        
        >>> parse_url('')
        (None, None, None)
    """
    if not url:
        return None, None, None
        
    # Split query parameters
    url_parts = url.split('?', 1)
    base = url_parts[0]
    query = f"?{url_parts[1]}" if len(url_parts) > 1 else None
    
    # Extract page number using regex
    page_match = re.search(r'/page/(\d+)/?', base)
    page_number = int(page_match.group(1)) if page_match else None
    
    # Clean up base URL
    base_url = re.sub(r'/page/\d+/?', '', base).strip('/')
    
    return base_url, page_number, query
