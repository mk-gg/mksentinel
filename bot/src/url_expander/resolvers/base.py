from abc import ABC, abstractmethod
from typing import Optional, Set, ClassVar
from urllib.parse import urlparse
from ..core.exceptions import ResolverError


class URLResolver(ABC):
    """Abstract base class for URL resolvers"""
    
    @abstractmethod
    def can_handle(self, url: str) -> bool:
        """Check if this resolver can handle the given URL"""
        pass
    
    @abstractmethod
    def resolve(self, url: str) -> str:
        """Resolve the URL to its expanded form"""
        pass

class MultiDomainResolver(URLResolver):
    """Base class for resolvers that can handle multiple domains"""
    
    # Class variable to store supported domains
    DOMAINS: ClassVar[Set[str]] = set()
    
    @classmethod
    def register_domains(cls, *domains: str) -> None:
        """Register domains that this resolver can handle"""
        cls.DOMAINS.update(domains)

    @classmethod
    def can_handle(self, url: str) -> bool:
        """Check if this resolver can handle the given URL"""
        try:
            domain = urlparse(url).netloc.lower()
            return any(
                registered_domain in domain 
                for registered_domain in self.DOMAINS
            )
        except Exception:
            return False
    
