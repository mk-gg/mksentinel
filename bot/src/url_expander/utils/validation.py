from urllib.parse import urlparse
from typing import Optional, Tuple

def is_valid_url(url: str) -> Tuple[bool, Optional[str]]:
    """
    Validate URL format and return tuple of (is_valid, error_message)
    """
    try:
        result = urlparse(url)
        if not all([result.scheme, result.netloc]):
            return False, "Missing scheme or netloc"
        if result.scheme not in ['http', 'https']:
            return False, "Invalid scheme"
        return True, None
    except Exception as e:
        return False, str(e)