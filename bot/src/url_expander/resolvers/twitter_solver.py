import re
import httpx
from .base import URLResolver
from ..core.exceptions import ResolverError

class TwitterSolver(URLResolver):
    """Generic resolver that handles standard HTTP redirects with improved error handling"""
    
    def __init__(self, timeout: int = 10, max_redirects: int = 10, retry_count: int = 3):
        self.timeout = timeout
        self.max_redirects = max_redirects
        self.retry_count = retry_count
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
    
    def can_handle(self, url: str) -> bool:
        return True  # Generic resolver handles any URL
    
    def resolve(self, url: str) -> str:
        last_error = None
   
        print(f"Twitter Resolver")
        for attempt in range(self.retry_count):
            try:
                with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                  
                    response = client.get(url, headers=self.headers, follow_redirects=False)
                    response.raise_for_status()
                    match = re.search(r"(?P<url>https?://[^\s]+)\"", response.text)
                    return match.group("url") if match else None
                    
     
                
            except httpx.TimeoutException as e:
                last_error = f"Timeout error (attempt {attempt + 1}/{self.retry_count}): {str(e)}"
                continue
            except httpx.NetworkError as e:
                last_error = f"Network error (attempt {attempt + 1}/{self.retry_count}): {str(e)}"
                continue
            except httpx.HTTPStatusError as e:
                last_error = f"HTTP error (attempt {attempt + 1}/{self.retry_count}): {str(e)}"
                continue
                
        raise ResolverError(f"Failed to resolve URL after {self.retry_count} attempts. Last error: {last_error}")