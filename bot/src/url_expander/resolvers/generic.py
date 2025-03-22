import requests
from requests.exceptions import RequestException
from .base import URLResolver
from ..core.exceptions import ResolverError

class GenericResolver(URLResolver):
    """Generic resolver that handles standard HTTP redirects"""
    
    def __init__(self, timeout: int = 10, max_redirects: int = 10):
        self.timeout = timeout
        self.max_redirects = max_redirects
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def can_handle(self, url: str) -> bool:
        return True  # Generic resolver handles any URL
    
    def resolve(self, url: str) -> str:
        try:
            # Try HEAD request first
            response = self.session.head(
                url,
                allow_redirects=True,
                timeout=self.timeout
            )
            if response.ok:
                return response.url
            
            # Fallback to GET if HEAD fails
            response = self.session.get(
                url,
                allow_redirects=True,
                timeout=self.timeout
            )
            return response.url
            
        except RequestException as e:
            raise ResolverError(f"Failed to resolve URL: {str(e)}")