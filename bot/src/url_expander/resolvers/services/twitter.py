from urllib.parse import urlparse
from ..base import URLResolver
from ..twitter_solver import TwitterSolver

class TwitterResolver(URLResolver):
    """Resolver for Twitter t.co links"""
    
    def can_handle(self, url: str) -> bool:
        return urlparse(url).netloc == 't.co'
    
    def resolve(self, url: str) -> str:
        resolver = TwitterSolver()
        return resolver.resolve(url)