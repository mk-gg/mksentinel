import random
from urllib.parse import urlparse
from typing import Set, Optional
from src.utils  import find_message_url
from src.url_expander import EnhancedURLExpander
from src.url_expander.resolvers.services.cloudflare import CloudflareResolver
from src.url_expander.resolvers.services.twitter import TwitterResolver
from src.url_expander.core.models import URLStatus
from src.config import Config



def clean_normalize_url_ai(url):

    """Use AI to clean and normalize URLs when regular cleaning fails."""
    from google import genai


    api_keys = Config.apikeys["gemini_keys"]  # Assuming your keys are in a list
    random.shuffle(api_keys) # Shuffle the keys to add randomization.
    
    for api_key in api_keys:
        try:

            client = genai.Client(api_key=api_key)

            prompt = f"""
            Task: Clean and normalize the following URL by:
            1. Removing any credentials (usernames, passwords, @symbols)
            2. Ensuring proper scheme (https://)
            3. Preserving the core domain and path
            4. Identifying any suspicious patterns

            URL: {url}

            Output ONLY the cleaned URL with no additional text or explanations.
            """

            response = client.models.generate_content_stream(
                model="gemini-2.0-flash",
                contents=prompt
            )

            result = ""
            for chunk in response:
                result += chunk.text

            return result.strip()

        except Exception as e:
            print(f"API key {api_key[:8]}... failed: {e}. Trying next key.") # print the first 8 characters of the key.
            continue  # Try the next API key

    print("All API keys failed.")
    return None  # Return None if all keys fail

class URLProcessor:
    def __init__(self, ignore_domains: set[str], verbose: bool = True):
        # Store domains in a set for O(1) lookup
        self.ignore_domains = {domain.lower() for domain in ignore_domains}
        
        # Initialize URL expander
        self.expander = EnhancedURLExpander(verbose=verbose)
        self.expander.add_resolver(CloudflareResolver)
        self.expander.add_resolver(TwitterResolver)


    def get_domain(self, url: str) -> Optional[str]:
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.split(':')[0].lower()
            return domain
        except Exception:
            return None

    def is_domain_ignored(self, url: str) -> bool:
        domain = self.get_domain(url)
        return domain in self.ignore_domains if domain else False

    def process_url(self, url: str) -> Optional[str]:
        try:
            final_url = find_message_url(url)
            if final_url:
                # Check domain before expanding
                if self.is_domain_ignored(url):
                    return url
                    
                print(f"Final cleaned URL: {final_url}")
                result = self.expander.expand_url(final_url)
                if result.status == URLStatus.ERROR:
                    cleaned_ai = clean_normalize_url_ai(url)
                    print(f"Cleaned by AI: {cleaned_ai}")
                return result.expanded_url
        except Exception as e:
            print(f"Error processing URL: {e}")
      
        
       