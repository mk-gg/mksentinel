class ExpanderError(Exception):
    """Base exception for URL expander errors"""
    pass

class URLValidationError(ExpanderError):
    """Raised when URL validation fails"""
    pass

class ResolverError(ExpanderError):
    """Raised when URL resolution fails"""
    pass