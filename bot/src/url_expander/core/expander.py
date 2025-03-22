# url_expander/core/expander.py
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
from typing import Dict, List, Optional, Type
from urllib.parse import urlparse

from ..core.models import ExpansionResult, URLStatus
from ..core.exceptions import URLValidationError, ResolverError
from ..resolvers.base import URLResolver, MultiDomainResolver
from ..resolvers.generic import GenericResolver
from ..utils.validation import is_valid_url
from ..utils.cleaning import URLCleaner

class EnhancedURLExpander:
    """Enhanced URL expander with support for both single and multi-domain resolvers"""
    
    def __init__(
        self,
        resolvers: Optional[List[Type[URLResolver]]] = None,
        concurrent_requests: int = 10,
        cache_size: int = 1000,
        verbose: bool = False
    ):
        # Initialize with default resolvers if none provided
        self.resolvers = resolvers or []
        self.concurrent_requests = concurrent_requests
        self.logger = self._setup_logger(verbose)
        
        # Initialize resolver instances and domain mapping
        self.resolver_instances: Dict[str, URLResolver] = {}
        self.domain_mapping: Dict[str, URLResolver] = {}
        self._initialize_resolvers()
        
        # Setup caching
        self._setup_cache(cache_size)
        
        # Always add generic resolver as fallback
        self.generic_resolver = GenericResolver()
    
    def _setup_logger(self, verbose: bool) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO if verbose else logging.WARNING)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger
    
    def _setup_cache(self, cache_size: int) -> None:
        """Setup LRU cache for URL resolution"""
        self.resolve_url = lru_cache(maxsize=cache_size)(self._resolve_url)
    
    def _initialize_resolvers(self) -> None:
        """Initialize resolver instances and build domain mapping"""
        for resolver_class in self.resolvers:
            # Create instance of resolver
            resolver_instance = resolver_class()
            resolver_name = resolver_class.__name__
            self.resolver_instances[resolver_name] = resolver_instance
            
            # Handle MultiDomainResolver differently
            if isinstance(resolver_instance, MultiDomainResolver):
                # Map all domains to this resolver
                for domain in resolver_instance.DOMAINS:
                    self.domain_mapping[domain.lower()] = resolver_instance
            else:
                # For regular resolvers, we'll check can_handle() at runtime
                self.resolver_instances[resolver_name] = resolver_instance
    
    def _get_resolver(self, url: str) -> URLResolver:
        """Get appropriate resolver for the URL"""
        try:
            domain = urlparse(url).netloc.lower()
            
            # First check domain mapping (for MultiDomainResolvers)
            if domain in self.domain_mapping:
                return self.domain_mapping[domain]
            
            # Then check regular resolvers
            for resolver in self.resolver_instances.values():
                if not isinstance(resolver, MultiDomainResolver) and resolver.can_handle(url):
                    return resolver
            
            # Fallback to generic resolver
            return self.generic_resolver
            
        except Exception as e:
            self.logger.error(f"Error getting resolver for {url}: {str(e)}")
            return self.generic_resolver
    
    def _resolve_url(self, url: str) -> ExpansionResult:
        """Core URL resolution logic"""
        # Validate URL
        is_valid, error = is_valid_url(url)
        if not is_valid:
            return ExpansionResult(
                original_url=url,
                expanded_url=url,
                status=URLStatus.ERROR,
                error=error or "Invalid URL format"
            )
        
        try:
            # Get appropriate resolver
            resolver = self._get_resolver(url)
            
            # Log which resolver is being used
            self.logger.debug(f"Using {resolver.__class__.__name__} for {url}")
            
            # Resolve and clean URL
            expanded_url = resolver.resolve(url)
            cleaned_url = URLCleaner.clean_url(expanded_url)
            
            return ExpansionResult(
                original_url=url,
                expanded_url=cleaned_url,
                status=URLStatus.SUCCESS
            )
            
        except ResolverError as e:
            self.logger.error(f"Resolver error for {url}: {str(e)}")
            return ExpansionResult(
                original_url=url,
                expanded_url=url,
                status=URLStatus.ERROR,
                error=str(e)
            )
        except Exception as e:
            self.logger.error(f"Unexpected error expanding {url}: {str(e)}")
            return ExpansionResult(
                original_url=url,
                expanded_url=url,
                status=URLStatus.ERROR,
                error=f"Unexpected error: {str(e)}"
            )
    
    def expand_urls(self, urls: List[str]) -> List[ExpansionResult]:
        """Expand multiple URLs concurrently"""
        if not urls:
            return []
        
        with ThreadPoolExecutor(max_workers=self.concurrent_requests) as executor:
            future_to_url = {
                executor.submit(self.resolve_url, url): url
                for url in urls
            }
            
            results = []
            for future in as_completed(future_to_url):
                results.append(future.result())
        
        return results

    def expand_url(self, url: str) -> ExpansionResult:
        """Expand a single URL"""
        return self.resolve_url(url)

    def add_resolver(self, resolver_class: Type[URLResolver]) -> None:
        """Add a new resolver at runtime"""
        resolver_instance = resolver_class()
        resolver_name = resolver_class.__name__
        
        if isinstance(resolver_instance, MultiDomainResolver):
            # Update domain mapping for MultiDomainResolver
            for domain in resolver_instance.DOMAINS:
                self.domain_mapping[domain.lower()] = resolver_instance
        
        # Add to resolver instances
        self.resolver_instances[resolver_name] = resolver_instance
        self.logger.info(f"Added new resolver: {resolver_name}")
    
    def remove_resolver(self, resolver_name: str) -> None:
        """Remove a resolver at runtime"""
        if resolver_name in self.resolver_instances:
            resolver = self.resolver_instances[resolver_name]
            
            # Remove from domain mapping if it's a MultiDomainResolver
            if isinstance(resolver, MultiDomainResolver):
                for domain in resolver.DOMAINS:
                    self.domain_mapping.pop(domain.lower(), None)
            
            # Remove from resolver instances
            del self.resolver_instances[resolver_name]
            self.logger.info(f"Removed resolver: {resolver_name}")