from requests.exceptions import RequestException
from .base import URLResolver
from ..core.exceptions import ResolverError
from curl_cffi import requests
from bs4 import BeautifulSoup


class SpecialResolver(URLResolver):
    """Special resolver that handles cloudflare HTTP redirects"""
    
    def __init__(self, timeout: int = 50, max_redirects: int = 10):
        self.timeout = timeout
        self.max_redirects = max_redirects
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
        })
    
    def can_handle(self, url: str) -> bool:
        return True  # Generic resolver handles any URL
    
    def resolve(self, url: str) -> str:
        """
        Resolves a URL to its final destination and extracts relevant metadata.
        
        Args:
            url: The URL to resolve
            
        Returns:
            str: The resolved URL or canonical link
            
        Raises:
            ResolverError: If the URL cannot be resolved
        """
        try:
            print(f'Special')
            
            # Make request with Chrome impersonation
            response = requests.get(
                url,
                impersonate="chrome",
                headers={
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                }
            )
            
            if response.status_code != 200:
                raise ResolverError(f"HTTP error {response.status_code}")
                
            # Parse the response
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Extract metadata
            metadata = {
                'final_url': response.url,
                'og_url': None,
                'canonical_link': None
            }
            
            # Try to get OpenGraph URL
            og_url = soup.find('meta', property='og:url')
            if og_url and og_url.get('content'):
                metadata['og_url'] = og_url['content']
                
            # Try to get canonical link
            canonical = soup.find('link', rel='canonical')
            if canonical and canonical.get('href'):
                metadata['canonical_link'] = canonical['href']
                
            # Debug output
            print("Final URL:", metadata['final_url'])
            print("OG URL:", metadata['og_url'] if metadata['og_url'] else "Not found")
            print("Canonical Link:", metadata['canonical_link'] if metadata['canonical_link'] else "Not found")
            
            # Return the best available URL in order of preference:
            # 1. Canonical link
            # 2. OpenGraph URL
            # 3. Final URL after redirects
            return (
                metadata['canonical_link'] or 
                metadata['og_url'] or 
                metadata['final_url'] or 
                url  # fallback to original URL if nothing else is available
            )
            
        except RequestException as e:
            raise ResolverError(f"Failed to resolve URL: {str(e)}")
        except Exception as e:
            raise ResolverError(f"Unexpected error while resolving URL: {str(e)}")