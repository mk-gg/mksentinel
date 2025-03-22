from urllib.parse import urlparse, ParseResult, parse_qs, urlencode

class URLCleaner:
    # Parameters to remove from URLs
    TRACKING_PARAMS = {
        'utm_source', 'utm_medium', 'utm_campaign',
        'utm_term', 'utm_content', 'fbclid',
        'gclid', '_ga'
    }
    
    @classmethod
    def clean_url(cls, url: str) -> str:
        """Clean URL by removing tracking parameters and normalizing"""
        parsed = urlparse(url)
        
        # Parse and clean query parameters
        if parsed.query:
            query_params = parse_qs(parsed.query)
            cleaned_params = {
                k: v for k, v in query_params.items()
                if k not in cls.TRACKING_PARAMS
            }
            query = urlencode(cleaned_params, doseq=True)
        else:
            query = ''
        
        # Reconstruct URL
        cleaned = ParseResult(
            scheme=parsed.scheme,
            netloc=parsed.netloc.lower(),
            path=parsed.path,
            params=parsed.params,
            query=query,
            fragment=''  # Remove fragments
        )
        
        return cleaned.geturl()