from ..base import MultiDomainResolver
from ..special import SpecialResolver

class CloudflareResolver(MultiDomainResolver):
    """Resolver for cloudflare links"""


    MultiDomainResolver.register_domains(
        'e.vg',
        'dsc.gg',
        'snl.ink',
        'short.gy',
        'meba.link',
        'discord.com',
        'easyurl.net',
        'discord.co',
        'discord.gg', 
        'discadia.com',
        "t2m.io", 
        'sur.li',
        'discordapp.com'

    )

    def resolve(self, url: str) -> str:
        # Special handling for Cloudflare protection
        resolver = SpecialResolver()
        # Add custom headers or other Cloudflare bypass methods
        return resolver.resolve(url)
