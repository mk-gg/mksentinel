import asyncio, glob, io, os, threading, re
import requests
import aiohttp, selfcord, httpx, urllib.parse

from PIL import Image, ImageDraw, ImageFont
from pilmoji import Pilmoji
from io import BytesIO
from os.path import join
from datetime import datetime, timedelta, timezone
from selfcord.ext import commands
from random import choice, uniform, randint
from collections.abc import AsyncGenerator, Generator
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, List

from rich.console import Console
from rich import print
from rich.panel import Panel

# from src.config import *


from src.url_expander import EnhancedURLExpander
from src.url_expander.resolvers.services.cloudflare import CloudflareResolver
from src.url_expander.resolvers.services.twitter import TwitterResolver

expander = EnhancedURLExpander(verbose=True)
expander.add_resolver(CloudflareResolver)
expander.add_resolver(TwitterResolver)




console = Console()

async def async_run(
    func, 
    *args: str, 
    **kwargs: str
    ) -> asyncio.Future:
    """
    await async_run(synchronous function, args, keyword args) -> asyncio future object

    Runs a synchronous function asynchronous

    :param func function: Synchronous function to run
    :param args str: Arguments
    :param kwargs str: Keyword arguments
    """

    loop = asyncio.get_event_loop()

    return await loop.run_in_executor(
        ThreadPoolExecutor(),
        lambda: func(*args, **kwargs)
    )

def async_wrap_iter(
    it: Generator
    ) -> AsyncGenerator:
    """
    async_wrap_iter(iterable) -> async generator

    Turns a synchronous iterable into an asynchronous generator

    :param it Generator: Generator
    :returns AsyncGenerator: Asynchronous generator
    """

    loop = asyncio.get_event_loop()
    q = asyncio.Queue(1)

    exception = None
    _END = object()

    async def yield_queue_items() -> AsyncGenerator:
        """
        await yield_queue_items() -> async generator

        Yields all the items from the queue

        :returns AsyncGenerator: Asynchronous generator
        """

        while 1:
            next_item = await q.get()

            if next_item is _END:
                break

            yield next_item

        if exception is not None:
            # the iterator has raised, propagate the exception
            raise exception

    def iter_to_queue() -> None:
        """
        iter_to_queue() -> nothing

        Moves all the items from the iterable into the queue

        :returns None: Nothing
        """

        nonlocal exception

        try:
            for item in it:

                # This runs outside the event loop thread, so we
                # must use thread-safe API to talk to the queue.
                asyncio.run_coroutine_threadsafe(
                    q.put(item), 
                    loop
                ).result()

        except Exception as e:
            exception = e

        finally:
            asyncio.run_coroutine_threadsafe(
                q.put(_END), 
                loop
            ).result()

    threading.Thread(
        target=iter_to_queue
    ) .start()

    return yield_queue_items()

def get_size(
    _bytes: int | float, 
    suffix = "B"
    ) -> str:
    """
    get_size(bytes, suffix) -> proper unit

    Gets the proper unit for the bytes

    :param bytes int or float: Bytes
    :param suffix str: Suffix to prepend
    :returns str: String with proper unit and suffix prepended
    """

    factor = 1024
    for unit in ["", "Ki", "Mi", "Gi", "Te", "Pe"]:
        
        if _bytes < factor:
            return f'{_bytes:.2f}{unit}{suffix}'

        _bytes /= factor
    
    return ''

def clear() -> None:
    """
    clear() -> nothing

    Clears the screen, thats it

    :returns None: Nothing
    """

    print('\033c', end='')

async def load_cogs(
    client: commands.Bot
    ) -> None:
    """
    await load_cogs(client) -> nothing

    Loads all cogs in the "src/cogs" directory

    :param client commands.Bot: The connected discord bot/client
    :returns None: Nothing
    """

    for file in glob.glob(join('src', 'cogs', '*')):
        if file.endswith('.py') and not '__' in file and not file.endswith('.disabled.py'):
            file = file.replace(os.sep, '.')[:-3]
            
            console.log(f'[#307866]Loading cog --> {file}')
            
            try:
                await client.load_extension(file)

            except commands.errors.ExtensionAlreadyLoaded:
                await client.unload_extension(file)
                await client.load_extension(file)

            except Exception as e:
                print(f'[red]Exception while loading cog "{file}"> {str(e).rstrip()}\n')
                continue

async def unload_cog(
    client: commands.Bot,
    cog: str
    ) -> bool | None | Exception:
    """
    await unload_cog(client, cog name) -> status

    Unloads the given cog

    :param client commands.Bot: The connected discord bot/client
    :param cog str: Cog name
    :returns bool or Exception: True if the cog was unloaded, False if not found and an Exception if any errors where raised
    """

    for file in glob.glob(join('src', 'cogs', '*')):
        if cog in file:
            file = file.replace(os.sep, '.')[:-3]

            try:
                await client.unload_extension(file)

                return True
            except Exception as e:
                return e
    
    return False

def randomstr(
    length: int, 
    chars: str | list = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM0123456789"
    ) -> str:
    """
    randomstr(length, allowed characters) -> created string

    Builds a random string

    :param length int: Length of the string
    :param chars str or list: Characters to pick from
    """

    return ''.join([choice(chars) for _ in range(length)])


def has_multiple_new_lines(text): return len([line for line in text.splitlines() if line.strip()]) > 1

def combine_lines(text):
    return ''.join(line.strip() for line in text.splitlines())


def translate_confusable_characters(input_string):
    """
    Converts each special matching unicode to a normal letter unicode.
    
    https://util.unicode.org/UnicodeJsps/confusables.jsp?a=B&r=None
    """

    
    alphabet_map = {
    ".": ['｡'],
    
    "a": ['ɑ', 'α', 'а', '⍺', '𝐚', '𝑎', '𝒂', '𝒶', '𝓪', '𝔞', '𝕒', '𝖆', '𝖺', '𝗮', '𝘢', '𝙖', '𝚊', '𝛂', '𝛼', '𝜶', '𝝰', '𝞪', 'ａ'],
    "A": ['Ａ', 'ᗅ', 'Α', 'А', 'Ꭺ', 'ꓮ', '𝐀', '𝐴', '𝑨', '𝒜', '𝓐', '𝔸', '𝖠', '𝗔', '𝘈', '𝔄', '𝘼', '𝙰', '𝚨', '𝛢', '𝜜', '𝝖', '𝞐'],

    "b": ['Ƅ', 'Ь', 'Ꮟ', 'ᑲ', 'ᖯ', '𝐛', '𝑏', '𝒃', '𝒷', '𝓫', '𝔟', '𝕓', '𝖇', '𝖻', '𝗯', '𝘣', '𝙗', '𝚋'],
    "B": ['Β', 'В', 'Ᏼ', 'ᗷ', 'ℬ', 'ꓐ', 'Ꞵ', '𐊂', '𐊡', '𐌁', '𝐁', '𝐵', '𝑩', '𝓑', '𝔅', '𝔹', '𝕭', '𝖡', '𝗕', '𝘉', '𝘽', '𝙱', '𝚩', '𝛣', '𝜝', '𝝗', '𝞑', 'Ｂ'],

    "c": ['ϲ', 'с', 'ᴄ', 'ⅽ', 'ⲥ', 'ꮯ', '𐐽', '𝐜', '𝑐', '𝒄', '𝒸', '𝓬', '𝔠', '𝕔', '𝖈', '𝖼', '𝗰', '𝘤', '𝙘', '𝚌', 'ｃ'],
    "C": ['Ϲ', 'С', 'Ꮯ', 'ℂ', 'ℭ', 'Ⅽ', 'Ⲥ', 'ꓚ', '𐊢', '𐌂', '𐐕', '𝐂', '𝐶', '𝑪', '𝒞', '𝓒', '𝕮', '𝖢', '𝗖', '𝘊', '𝘾', '𝙲', '🝌', 'Ｃ'],

    "d": ['ԁ', 'Ꮷ', 'ᑯ', 'ⅆ', 'ⅾ', 'ⅾ', '𝐝', '𝑑', '𝒅', '𝒹', '𝓭', '𝔡', '𝕕', '𝖉', '𝖽', '𝗱', '𝘥', '𝙙', '𝚍'],
    "D": ['Ꭰ', 'ᗞ', 'ᗪ', 'ⅅ', 'Ⅾ', 'ꓓ', '𝐃', '𝐷', '𝑫', '𝒟', '𝓓', '𝔇', '𝔻', '𝕯', '𝖣', '𝗗', '𝘋', '𝘿', '𝙳'],

    "e": ['е', 'ҽ', '℮', 'ℯ', 'ⅇ', 'ꬲ', '𝐞', '𝑒', '𝒆', '𝓮', '𝔢', '𝕖', '𝖊', '𝖾', '𝗲', '𝘦', '𝙚', '𝚎', 'ｅ'],
    "E": ['Ε', 'Е', 'Ꭼ', 'ℰ', '⋿', 'ⴹ', 'ꓰ', '𐊆', '𝐄', '𝐸', '𝑬', '𝓔', '𝔈', '𝔼', '𝕰', '𝖤', '𝗘', '𝘌', '𝙀', '𝙴', '𝚬', '𝛦', '𝜠', '𝝚', '𝞔', 'Ｅ'],

    "f": ['ſ', 'ẝ', 'ꞙ', 'ꞙ', '𝐟', '𝑓', '𝒇', '𝒻', '𝓯', '𝔣', '𝕗', '𝖋', '𝖿', '𝗳', '𝘧', '𝙛', '𝚏'],
    "F": ['Ϝ', 'ᖴ', 'ℱ', 'ꓝ', 'Ꞙ', '𐊇', '𐊥', '𝐅', '𝐹', '𝑭', '𝓕', '𝔉', '𝔽', '𝕱', '𝖥', '𝗙', '𝘍', '𝙁', '𝙵', '𝟊'],

    "g": ['ƍ', 'ɡ', 'ց', 'ᶃ', 'ℊ', '𝐠', '𝑔', '𝒈', '𝓰', '𝔤', '𝕘', '𝖌', '𝗀', '𝗴', '𝘨', '𝙜', '𝚐', 'ｇ'],
    "G": ['G', 'Ꮐ', 'Ᏻ', 'ꓖ', '𝐆', '𝐺', '𝑮', '𝒢', '𝓖', '𝔊', '𝔾', '𝕲', '𝖦', '𝗚', '𝘎', '𝙂', '𝙶'],

    "h": ['һ', 'հ', 'Ꮒ', 'ℎ', '𝐡', '𝒉', '𝒽', '𝓱', '𝔥', '𝕙', '𝖍', '𝗁', '𝗵', '𝘩', '𝙝', '𝚑', 'ｈ'],
    "H": ['Η', 'Н', 'Ꮋ', 'ᕼ', 'ℋ', 'ℌ', 'ℍ', 'Ⲏ', 'ꓧ', '𐋏', '𝐇', '𝐻', '𝑯', '𝓗', '𝕳', '𝖧', '𝗛', '𝘏', '𝙃', '𝙷', '𝚮', '𝛨', '𝜢', '𝝜', '𝞖', 'Ｈ'],

    "i": ['i', 'ı', 'ɩ', 'ι', 'і', 'Ꭵ', 'ℹ', 'ⅈ', 'ⅰ', '⍳', 'ꙇ', 'ꭵ', '𝐢', '𝑖', '𝒊', '𝒾', '𝓲', '𝔦', '𝕚', '𝖎', '𝗂', '𝗶', '𝘪', '𝙞', '𝚒', '𝚤', '𝛊', '𝜄', '𝜾', '𝝸', '𝞲', 'ｉ'],
    "I": ['ɪ', 'Ɩ', 'ǀ', 'Ι', 'Ι', 'І', 'Ӏ', '׀', 'ו', 'ן', 'ا', 'ߊ', 'ᛁ', 'ℐ', 'ℑ', 'I', '𝐈', '𝙸', 'ӏ'],

    "j": ['ϳ', 'ј', 'ⅉ', '𝐣', '𝑗', '𝒋', '𝒿', '𝓳', '𝔧', '𝕛', '𝖏', '𝗃', '𝗷', '𝘫', '𝙟', '𝚓', 'ｊ'],
    "J": ['Ϳ', 'Ϳ', 'Ј', 'Ꭻ', 'ᒍ', 'ꓙ', 'Ʝ', '𝐉', '𝐽', '𝑱', '𝒥', '𝓙', '𝔍', '𝕁', '𝕵', '𝖩', '𝗝', '𝘑', '𝙅', '𝙹', 'Ｊ'],

    "k": ['𝐤', '𝑘', '𝒌', '𝓀', '𝓴', '𝔨', '𝕜', '𝖐', '𝗄', '𝗸', '𝘬', '𝙠', '𝚔'],
    "K": ['Κ', 'К', 'Ꮶ', 'ᛕ', 'K', 'Ⲕ', 'ꓗ', '𝐊', '𝐾', '𝑲', '𝒦', '𝓚', '𝔎', '𝕂', '𝕶', '𝖪', '𝗞', '𝘒', '𝙆', '𝙺', '𝚱', '𝛫', '𝜥', '𝝟', '𝞙', 'Ｋ'],

    "l": ['l', 'Ɩ', 'ǀ', '١', '۱', 'ℓ', 'ⅼ', '∣', 'Ⲓ', 'ⵏ', 'ꓲ', '𐊊', '𐌉', '𐌠', '𝐥', '𝐼', '𝑙', '𝑰', '𝒍', '𝓁', '𝓘', '𝓵', '𝔩', '𝕀', '𝕝', '𝕴', '𝖑', '𝖨', '𝗅', '𝗜', '𝗹', '𝘐', '𝘭', '𝙄', '𝙡', '𝚕', '𝚰', '𝛪', '𝜤', '𝝞', '𝞘', 'ﺍ', 'ﺎ', 'ｌ', '￨'],
    "L": ['Ꮮ', 'ᒪ', 'ℒ', 'Ⅼ', 'Ⳑ', 'ꓡ', '𐐛', '𝐋', '𝐿', '𝑳', '𝓛', '𝔏', '𝕃', '𝕷', '𝖫', '𝗟', '𝘓', '𝙇', '𝙻'],

    "m": ['ⅿ', '𝐦', '𝑚', '𝒎', '𝓂', '𝓶', '𝔪', '𝕞', '𝖒', '𝗆', '𝗺', '𝘮', '𝙢', '𝚖'],
    "M": ['Μ', 'Ϻ', 'М', 'Ꮇ', 'ᗰ', 'ᛖ', 'ℳ', 'Ⅿ', 'Ⲙ', 'ꓟ', '𐊰', '𐌑', '𝐌', '𝑀', '𝑴', '𝓜', '𝔐', '𝕄', '𝕸', '𝖬', '𝗠', '𝘔', '𝙈', '𝙼', '𝚳', '𝛭', '𝜧', '𝝡', '𝞛', 'Ｍ'],

    "n": ['ո', 'ռ', '𝐧', '𝑛', '𝒏', '𝓃', '𝓷', '𝔫', '𝕟', '𝖓', '𝗇', '𝗻', '𝘯', '𝙣', '𝚗'],
    "N": ['Ν', 'ℕ', 'Ⲛ', 'ꓠ', '𝐍', '𝑁', '𝑵', '𝒩', '𝓝', '𝔑', '𝕹', '𝖭', '𝗡', '𝘕', '𝙉', '𝙽', '𝚴', '𝛮', '𝜨', '𝝢', '𝞜', 'Ｎ'],

    "o": ['ο', 'σ', 'о', 'օ', 'ס', 'ه', '٥', '०', '੦', '૦', '௦', '౦', '೦', 'ഠ', '൦', '๐', '໐', 'ဝ', '၀', 'ჿ', 'ᴏ', 'ᴑ', 'ℴ', 'ⲟ', 'ꬽ', '𐐬', '𐓪', '𝐨', '𝑜', '𝒐', '𝓸', '𝔬', '𝕠', '𝖔', '𝗈', '𝗼', '𝘰', '𝙤', '𝚘', '𝛐', '𝛔', '𝜊', '𝜎', '𝝄', '𝝈', '𝝾', '𝞂', '𝞸', '𝞼', 'ｏ'],
    "O": ['০', '߀', 'ଠ', '୦', 'ዐ', 'ⵔ', '〇', 'ꓳ', '𐊒', '𐊫', '𝐎', '𝑂', '𝑶', '𝒪', '𝓞', '𝔒', '𝕆', '𝕺', '𝖮', '𝗢', '𝙊', '𝙾', '𝚶', '𝛰', '𝜪', '𝝤', '𝞞', '𝟎', '𝟘', '𝟢', '𝟬', '𝟶', 'Ｏ', 'О', 'Ο'],

    "p": ['ρ', 'ϱ', 'р', '⍴', 'ⲣ', '𝐩', '𝑝', '𝒑', '𝓅', '𝓹', '𝔭', '𝕡', '𝖕', '𝗉', '𝗽', '𝘱', '𝙥', '𝚙', '𝛒', '𝛠', '𝜌', '𝜚', '𝝆', '𝝔', '𝞀', '𝞎', '𝞺', '𝟈', 'ｐ'],
    "P": ['Ρ', 'Р', 'Ꮲ', 'ᑭ', 'ℙ', 'Ⲣ', 'ꓑ', '𐊕', '𝐏', '𝑃', '𝑷', '𝒫', '𝓟', '𝔓', '𝕻', '𝖯', '𝗣', '𝘗', '𝙋', '𝙿', '𝚸', '𝛲', '𝜬', '𝝦', '𝞠', 'Ｐ'],

    "q": ['ԛ', 'գ', 'զ', '𝐪', '𝑞', '𝒒', '𝓆', '𝓺', '𝔮', '𝕢', '𝖖', '𝗊', '𝗾', '𝘲', '𝙦', '𝚚'],
    "Q": ['ℚ', 'ⵕ', '𝐐', '𝑄', '𝑸', '𝒬', '𝓠', '𝔔', '𝕼', '𝖰', '𝗤', '𝘘', '𝙌', '𝚀'],

    "r": ['г', 'ᴦ', 'ⲅ', 'ꭇ', 'ꭈ', 'ꮁ', '𝐫', '𝑟', '𝒓', '𝓇', '𝓻', '𝔯', '𝕣', '𝖗', '𝗋', '𝗿', '𝘳', '𝙧', '𝚛'],
    "R": ['Ʀ', 'Ꭱ', 'Ꮢ', 'ᖇ', 'ℛ', 'ℜ', 'ℝ', 'ꓣ', '𐒴', '𝐑', '𝑅', '𝑹', '𝓡', '𝕽', '𝖱', '𝗥', '𝘙', '𝙍', '𝚁'],

    "s": ['ƽ', 'ѕ', 'ꜱ', 'ꮪ', '𐑈', '𝐬', '𝑠', '𝒔', '𝓈', '𝓼', '𝔰', '𝕤', '𝖘', '𝗌', '𝘀', '𝘴', '𝙨', '𝚜', 'ｓ'],
    "S": ['Ѕ', 'Տ', 'Ꮥ', 'Ꮪ', 'ꓢ', '𐊖', '𐐠', '𝐒', '𝑆', '𝑺', '𝒮', '𝓢', '𝔖', '𝕊', '𝕾', '𝖲', '𝗦', '𝘚', '𝙎', '𝚂', 'Ｓ'],

    "t": ['𝐭', '𝑡', '𝒕', '𝓉', '𝓽', '𝔱', '𝕥', '𝖙', '𝗍', '𝘁', '𝘵', '𝙩', '𝚝'],
    "T": ['Τ', 'Т', 'Ꭲ', '⊤', '⟙', 'Ⲧ', 'ꓔ', '𐊗', '𐊱', '𐌕', '𝐓', '𝑇', '𝑻', '𝒯', '𝓣', '𝔗', '𝕋', '𝕿', '𝖳', '𝗧', '𝘛', '𝙏', '𝚃', '𝚻', '𝛵', '𝜯', '𝝩', '𝞣', '🝨', 'Ｔ'],

    "u": ['ʋ', 'υ', 'ս', 'ᴜ', 'ꞟ', 'ꭎ', 'ꭒ', '𐓶', '𝐮', '𝑢', '𝒖', '𝓊', '𝓾', '𝔲', '𝕦', '𝖚', '𝗎', '𝘂', '𝘶', '𝙪', '𝚞', '𝛖', '𝜐', '𝝊', '𝞄', '𝞾'],
    "U": ['Ս', 'ሀ', 'ᑌ', '∪', '⋃', 'ꓴ', '𐓎', '𝐔', '𝑈', '𝑼', '𝒰', '𝓤', '𝔘', '𝕌', '𝖀', '𝖴', '𝗨', '𝘜', '𝙐', '𝚄'],

    "v": ['ѵ',  'ט', 'ᴠ', 'ⅴ', '∨', '⋁', 'ꮩ', '𝐯', '𝑣', '𝒗', '𝓋', '𝓿', '𝔳', '𝕧', '𝖛', '𝗏', '𝘃', '𝘷', '𝙫', '𝚟', 'v', '𝜈', '𝝂', '𝝼', '𝞶', 'ｖ'],
    "V": ['٧', '۷', 'ᐯ', 'ⴸ', 'ꓦ', '𝐕', '𝑉', '𝑽', '𝒱', '𝓥', '𝔙', '𝕍', '𝖁', '𝖵', '𝗩', '𝘝', '𝙑', '𝚅', 'Ꮩ'],

    "w": ['ɯ', 'ѡ', 'ԝ', 'ա', 'ᴡ', 'ꮃ', '𝐰', '𝑤', '𝒘', '𝓌', '𝔀', '𝔴', '𝕨', '𝖜', '𝗐', '𝘄', '𝘸', '𝙬', '𝚠'],
    "W": ['Ꮤ', 'ꓪ', '𝐖', '𝑊', '𝑾', '𝒲', '𝓦', '𝔚', '𝕎', '𝖂', '𝖶', '𝗪', '𝘞', '𝙒', '𝚆'],

    "x": ['×', 'х', 'ᕁ', 'ᕽ', '᙮', 'ⅹ', '⤫', '⤬', '⨯', '𝐱', '𝑥', '𝒙', '𝓍', '𝔁', '𝔵', '𝕩', '𝖝', '𝗑', '𝘅', '𝘹', '𝙭', '𝚡', 'ｘ'],
    "X": ['Χ', '᙭', 'ᚷ', '╳', 'Ⲭ', 'ⵝ', 'ꓫ', 'Ꭓ', '𐊐', '𐊴', '𐌗', '𐌢', '𝐗', '𝑋', '𝑿', '𝒳', '𝓧', '𝔛', '𝕏', '𝖃', '𝖷', '𝗫', '𝘟', '𝙓', '𝚇', '𝚾', '𝛸', '𝜲', '𝝬', '𝞦', 'Х'],

    "y": ['ɣ', 'ʏ', 'γ', 'у', 'ү', 'ყ', 'ᶌ', 'ỿ', 'ℽ', 'ꭚ', '𝐲', '𝑦', '𝒚', '𝓎', '𝔂', '𝔶', '𝕪', '𝖞', '𝗒', '𝘆', '𝘺', '𝙮', '𝚢', '𝛄', '𝛾', '𝜸', '𝝲', '𝞬', 'ｙ'],
    "Y": ['Υ', 'ϒ', 'У', 'Ү', 'Ꭹ', 'Ꮍ', 'Ⲩ', 'ꓬ', '𐊲', '𝐘', '𝑌', '𝒀', '𝒴', '𝓨', '𝔜', '𝕐', '𝖄', '𝖸', '𝗬', '𝘠', '𝙔', '𝚈', '𝚼', '𝛶', '𝜰', '𝝪', '𝞤', 'Ｙ'],

    "z": ['ᴢ', 'ꮓ', '𝐳', '𝑧', '𝒛', '𝓏', '𝔃', '𝕫', '𝗓', '𝘇', '𝘻', '𝙯', '𝚣'],
    "Z": ['Ζ', 'Ꮓ', 'ℤ', 'ꓜ', '𝐙', '𝑍', '𝒁', '𝒵', '𝓩', '𝖹', '𝗭', '𝘡', '𝙕', '𝚉', '𝚭', '𝛧', '𝜡', '𝝛', '𝞕', 'Ｚ']


    }


    # trans_table = {}
    # for k, chars in alphabet_map.items():
    #     for char in chars:
    #         if len(char) == 1:
    #             trans_table[char] = k
    #         else:
    #             print(f"Warning: Ignoring character '{char}' because it is not a single character.")
    # trans_table = str.maketrans(trans_table)
    # return input_string.translate(trans_table)

    trans_table = str.maketrans({k: char for char, variations in alphabet_map.items() for k in variations})
    return input_string.translate(trans_table)

def create_panel(url, category, guild_name, message, member):
    panel_message = (
        f"URL: [b]{url}[/]\n"
        f"Category: [b]{category}[/]\n"
        f"Guild name: [b]{guild_name}[/]\n"
        f"Message: [b]{message}[/]\n\n"
        f"Sender: [b]{member.name}[/]\n"
        f"UID: [b]{member.id}[/]" 
    )
    panel = Panel.fit(panel_message, width=60, padding=(1, 2), title="Warning", subtitle=f"- {member.guild} -")
    print(panel)

def get_time_now():
    return datetime.now().strftime("%H:%M:%S")

def check_date(input_date, day):
    """
    This function checks if the given date is within the specified number of days.
    
    Parameters:
    input_date (str): The date to check in the format "YYYY-MM-DD HH:MM:SS%z".
    day (int): The number of days within which the given date should be.
    
    Returns:
    bool: True if the given date is within the specified number of days, otherwise False.
    """

    given_date_str = input_date
    given_date = datetime.strptime(given_date_str, "%Y-%m-%d %H:%M:%S%z")
    current_date = datetime.now(timezone.utc)
    time_difference = current_date - given_date 
    return time_difference < timedelta(days=day)


# def find_message_url(message: str) -> Optional[str]:
#     """
#     Find and resolve the final URL in a given message.
    
#     Args:
#         message (str): The input message to extract URL from
    
#     Returns:
#         Optional[str]: The final resolved URL, or None if no URL is found
#     """
#     extracted_urls = extract_urls(message)
#     if extracted_urls:
#         print(f"URL FOOUND!")
#         for url in extracted_urls:
#             sanitized_url = clean_url(url)
#             if sanitized_url:
#                     return sanitized_url
#                 # fetched_final_url = get_final_url(sanitized_url)
#                 # if fetched_final_url:
#                     # return fetched_final_url
#     return None

def clean_normalize_url_ai(url):
    """Use AI to clean and normalize URLs when regular cleaning fails."""
    from google import genai

    client = genai.Client(api_key="AIzaSyCMpcoAPfmbiMISF6UxrZv242q9stqaQvg")
    
    prompt = f"""
    Task: Clean and normalize the following URL by:
    1. Removing any credentials (usernames, passwords, @symbols)
    2. Ensuring proper scheme (https://)
    3. Preserving the core domain and path
    4. Identifying any suspicious patterns

    URL: {url}

    Output ONLY the cleaned URL with no additional text or explanations.
    """

    try:
        response = client.models.generate_content_stream(
            model="gemini-2.0-flash",
            contents=prompt
        )
        
        result = ""
        for chunk in response:
            result += chunk.text
            
        return result.strip()
    except Exception as e:
        print(f"AI cleaning failed: {e}")
        return None

def find_message_url(message: str) -> Optional[str]:
    """
    Find and resolve the final URL in a given message.
    Uses regular cleaning first, then falls back to AI cleaning if needed.
    
    Args:
        message (str): The input message to extract URL from
    
    Returns:
        Optional[str]: The final resolved URL, or None if no URL is found
    """
    extracted_urls = extract_urls(message)
    if not extracted_urls:
        return None

    # print("URLs found!")
    
    for url in extracted_urls:
        # Try regular cleaning first
        sanitized_url = clean_url(url)
        
        if not sanitized_url:
            print(f"Regular cleaning failed for: {url}")
            print("Attempting AI cleaning...")
            sanitized_url = clean_normalize_url_ai(url)
        
        if sanitized_url:
            # Validate the AI-cleaned URL with our regular cleaner
            final_check = clean_url(sanitized_url)
            if final_check:
                return final_check
            return sanitized_url
            
    return None

def get_domain_name(url):
    parsed_url = urllib.parse.urlparse(url)
    # Extract the domain name

    domain_name = parsed_url.netloc

    return domain_name


# Example usage:
def find_and_process_message_url(message: str):
    """Example of how to use the URL finding and cleaning system."""
    try:
        final_url = find_message_url(message)
        if final_url:
            print(f"Final cleaned URL: {final_url}")
            
            result = expander.expand_url(final_url)
            if final_url == result.expanded_url:
                print(f"[red]URLStatus.ERROR[/red]: {result} was not expanded correctly.")
            else:
                print(f"[#A0C878]{result.status}[/]: {result.expanded_url}")
            return result.expanded_url
             
    except Exception as e:
        print(f"Error processing URL: {e}")




def create_message_panel(name, uid, reason, message, width=500, padding=15, avatar_url=None, 
                        show_title=True, max_chars=None, scale=1.0):
    """
    Create a message panel with options for truncation, scaling, and emoji support.
    """
    # Validate scale factor
    if scale not in [0.5, 0.8, 1.0, 2.0]:
        raise ValueError("Scale must be 0.5, 0.8, 1.0, or 2.0")
    
    # Apply scaling to base dimensions
    width = int(width * scale)
    padding = int(padding * scale)
    font_size = int(14 * scale)
    
    # Load font with fallback
    try:
        font = ImageFont.truetype("fonts/JetBrainsMono.ttf", font_size)
    except Exception:
        try:
            # Try system font as fallback
            font = ImageFont.truetype("Arial", font_size)
        except Exception:
            font = ImageFont.load_default()
    
    # Calculate scaled dimensions
    avatar_size = int(40 * scale)
    avatar_padding = int(20 * scale)
    
    # Truncate message if needed
    if max_chars and len(message) > max_chars:
        message = message[:max_chars-3] + "..."
    
    # Prepare the fields
    fields = [
        f"Username: {name}",
        f"UID: {uid}",
        f"Reason: {reason}",
        "Sent Message:",
    ]
    
    def calculate_text_size(text, font, pilmoji):
        """Helper function to calculate text dimensions with Pilmoji"""
        test_img = Image.new('RGBA', (width * 2, font_size * 2), (0, 0, 0, 0))
        with Pilmoji(test_img) as p:
            return p.getsize(text, font)
    
    def get_wrapped_text(text, font, max_width):
        """Simplified text wrapping function"""
        words = text.split()
        lines = []
        current_line = []
        current_width = 0
        
        for word in words:
            # Calculate word width including space
            word_with_space = word + " "
            word_width = calculate_text_size(word_with_space, font, Pilmoji)[0]
            
            if current_width + word_width <= max_width:
                current_line.append(word)
                current_width += word_width
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
                current_width = calculate_text_size(word + " ", font, Pilmoji)[0]
        
        if current_line:
            lines.append(" ".join(current_line))
        
        return lines
    
    # Calculate available width for text
    available_width = width - (padding * 2)
    if avatar_url:
        available_width -= (avatar_size + avatar_padding)
    
    # Calculate layout dimensions
    title_height = int(30 * scale) if show_title else 0
    line_height = int(20 * scale)
    spacing = int(10 * scale)
    
    # Create temporary image for text wrapping
    temp_img = Image.new('RGBA', (width, 100), (26, 26, 26, 255))
    with Pilmoji(temp_img) as pilmoji:
        wrapped_message = get_wrapped_text(message, font, available_width)
    
    # Calculate total height
    fields_height = len(fields) * line_height
    message_height = len(wrapped_message) * line_height
    total_height = title_height + fields_height + spacing + message_height + (padding * 2)
    
    # Create final image
    img = Image.new('RGBA', (width, total_height), (26, 26, 26, 255))
    draw = ImageDraw.Draw(img)
    
    # Draw border
    border_width = max(1, int(2 * scale))
    draw.rectangle([(0, 0), (width-1, total_height-1)], outline='#666666', width=border_width)
    
    # Draw title bar
    if show_title:
        draw.rectangle([(border_width, border_width), 
                       (width-border_width-1, title_height-1)], 
                       fill='#333333')
        
        with Pilmoji(img) as pilmoji:
            pilmoji.text((padding, int(8 * scale)), 
                        "Message Details", 
                        font=font, 
                        fill='white')
    
    # Handle avatar
    if avatar_url:
        try:
            response = requests.get(avatar_url, 
                                  headers={'User-Agent': 'Mozilla/5.0'}, 
                                  timeout=5)
            response.raise_for_status()
            
            avatar_img = Image.open(BytesIO(response.content))
            avatar_img = avatar_img.resize((avatar_size, avatar_size))
            
            # Create circular mask
            mask = Image.new('L', (avatar_size, avatar_size), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse((0, 0, avatar_size, avatar_size), fill=255)
            
            # Apply mask
            output = Image.new('RGBA', (avatar_size, avatar_size), (0, 0, 0, 0))
            output.paste(avatar_img, (0, 0))
            output.putalpha(mask)
            
            # Place avatar
            avatar_x = width - avatar_size - avatar_padding
            avatar_y = title_height + padding
            img.paste(output, (avatar_x, avatar_y), output)
            
        except Exception as e:
            print(f"Failed to load avatar: {e}")
    
    # Draw fields and message
    with Pilmoji(img) as pilmoji:
        # Draw fields
        y = title_height + padding
        for field in fields:
            pilmoji.text((padding, y), field, font=font, fill='white')
            y += line_height
        
        y += spacing
        
        # Draw message
        for line in wrapped_message:
            pilmoji.text((padding, y), line, font=font, fill='white')
            y += line_height
    
    return img

def clean_url(url: str) -> str:
    """Clean and normalize URLs."""
    try:
        # Handle empty or invalid URLs
        if not url or url.isspace():
            return ''


        # Remove common Discord message formatting
        url = re.sub(r'[`*~]', '', url)
        url = url.strip('[]()<>"\' \t')


        # Handle URLs that start with multiple "http(s)://"
        url = re.sub(r'^https?://+(?=https?://)', '', url)

        # Handle all variants of encoded @ symbols and cleanup
        url = re.sub(r'(?:%40|@@?|!@!|%0%40|%0%400000|/%40%20@|%20@)', '@', url)
        url = re.sub(r'\.>?$', '', url)  # Remove trailing dot and optional angle bracket
        
        # Clean up multiple forward slashes, but preserve http(s)://
        url = re.sub(r'(?<!:)/{2,}', '/', url)

        # Trim any trailing characters after the URL
        url_match = re.match(r'(https?://\S+)', url)
        if url_match:
            url = url_match.group(1)

        # Handle words connected to discord.com
        url = re.sub(r'([a-zA-Z0-9]+)discord(?:app)?\.(?:com|gg|net)', 'discord.com', url, flags=re.IGNORECASE)

        # Handle Discord invite links specifically
        discord_match = re.search(r'(?:discord\.(?:com|gg)|discordapp\.com)/invite\??([a-zA-Z0-9]+)', url)
        if discord_match:
            return f'https://discord.gg/{discord_match.group(1)}'

        # Basic URL cleanup
        url = re.sub(r':discord\.', 'discord.', url)
        url = re.sub(r'\\+', '/', url)  # Replace backslashes with forward slashes
        
        # Decode URL-encoded characters before parsing
        url = urllib.parse.unquote(url)
        
        # Clean @ symbols and credentials
        url = re.sub(r'https?://[^@]+@', 'https://', url)
        
        # Ensure proper scheme
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url.lstrip('/:')
        
        # Parse and reconstruct URL
        parsed = urllib.parse.urlparse(url)
        netloc = parsed.netloc.split('@')[-1]  # Remove any remaining credentials
        
        # Handle specific Discord domain patterns
        netloc = re.sub(r'^([a-zA-Z0-9]+)discord\.', 'discord.', netloc, flags=re.IGNORECASE)
        
        # Clean path - remove duplicate slashes but preserve underscores and hyphens
        path = re.sub(r'/{2,}', '/', parsed.path)
        path = re.sub(r'\.+$', '', path)
        
        # Reconstruct clean URL
        clean_url_result = urllib.parse.urlunparse((
            'https',  # Always use HTTPS
            netloc,
            path,
            '',  # params
            '',  # query
            ''   # fragment
        ))
        
        # Final cleanup
        clean_url_result = re.sub(r'/$', '', clean_url_result)  # Remove trailing slash
        
        # Handle any remaining double https:// that might have been introduced
        clean_url_result = re.sub(r'^https://+(?=https?://)', '', clean_url_result)
        clean_url_result = re.sub(r'https://https:', 'https://', clean_url_result)
        return clean_url_result if clean_url_result != 'https://' else ''
        
    except Exception as e:
        print(f"Error cleaning URL: {e}")
        return ''


def extract_urls(message: str) -> List[str]:
    """Extract URLs from message content."""
    try:


        # Remove Discord mentions and formatting
        message = re.sub(r'<@!?\d+>|@everyone|@here', '', message)
        
        # Comprehensive URL extraction patterns
        url_patterns = [
                        # Handle URLs with encoded @ symbols and unusual patterns
            r'https?:/?/?(?:%40|@@?|!@!|%0%40|%0%400000|/%40%20@|%20@)?[^\s()<>]+',
            
            # Discord-specific patterns
            r'(?:desk)?discord\.(?:com|gg|net)/invite\\?/?[a-zA-Z0-9]+',
            r'[a-zA-Z0-9]+discord(?:app)?\.(?:com|gg|net)\S*',
            
            # URLs in angle brackets (with optional asterisks)
            r'\*?\*?<(https?:[^>]+)>\*?\*?',
            
            # Regular URLs with potential additional characters

            # Handles URLs with potential additional characters
            r'https?://[^\s)>]+',
            # Discord invites
            r'(?:discord\.(?:com|gg)|discordapp\.com)/invite\??[a-zA-Z0-9]+',
            # URLs in markdown
            r'\[([^\]]+)\]\(([^)]+)\)',
            # Domain patterns
            r'\b(?:www\.|\w+\.(?:com|org|net|edu|gov|io|gg|me|t\.co))\S+'
        ]
        
        urls = []
        for pattern in url_patterns:
            matches = re.finditer(pattern, message, re.IGNORECASE)
            for match in matches:
                # Handle different match groups for different patterns
                url = match.group(0) if len(match.groups()) == 0 else match.group(2) if len(match.groups()) == 2 else match.group(0)
                
                cleaned_url = clean_url(url)
                if cleaned_url and cleaned_url not in urls:
                    urls.append(cleaned_url)
        
        return urls
        
    except Exception as e:
        print(f"Error extracting URLs: {e}")
        return []

def get_final_url(url: str) -> Optional[str]:
    """Resolve the final URL after potential redirects."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }

    url = url if url.startswith('http') else f'https://{url}'

    try:
        with httpx.Client(timeout=50.0, follow_redirects=True) as client:
            if url.startswith('https://t.co/'):
                response = client.get(url, headers=headers, follow_redirects=False)
                response.raise_for_status()
                match = re.search(r"(?P<url>https?://[^\s]+)\"", response.text)
                return match.group("url") if match else None
            else:
                response = client.get(url, headers=headers)
                response.raise_for_status()
                return str(response.url)
    except Exception as err:
        print(f'An error occurred while resolving URL: {err}')
        return None

async def printlog(data, event='', reason=''):
    from src.config import Config
    time_format = f"[{get_time_now()}]"
    
    event_formats = {
        'ban': "[#f595ad]BAN[/]",
        'kick': "[#ffcc00]KICK[/]",
        'message': "[#EFE9D5]MESSAGE[/]",
        'join': "[#F5F5F5]JOIN[/]",

        # Add more events as needed

    }
    event_format = event_formats.get(event, '')
    
    

    # Check if the guild exists in the config
    if str(data['guild'].id) in Config.guilds:
        guild_color = Config.guilds[str(data['guild'].id)]['color']
        guild_format = f"[[{guild_color}]{data['guild']}[/]]"
        print(f"{time_format} {guild_format} [{event_format}] {data['member']} | {data['member'].display_name}  {data['message']}  {reason}  ({data['member'].id})")
    # else:
    #     print(f"{time_format} Guild ID {guild.id} not found in config.")

def print_guilds():

    for guild_id, data in Config.guilds.items():

        print(f'Guild ID: {guild_id}, Ban Channel: {data["ban_channel"]}, Color: {data["color"]}')

async def sendmsg(
    ctx, 
    message: str = '',
    edit_after: bool = True,
    img: str | None = None
    ) -> bool:
    """
    await sendmsg(context, message, edit afterwards) -> status

    Sends a message, and adds some randomization to the delays

    :param ctx object: Context
    :param message str: Message to send
    :param img str or None: Image to send from url, leave empty for no image
    :param edit_after bool: Edit the message so it doesn't raise suspicions
    :returns bool: True if everything succeeded, False if not
    """

    attachments = []
    if img:
        async with aiohttp.ClientSession() as session:
            async with session.get(img) as resp:
                
                if resp.status != 200:
                    await ctx.message.send('Could not download file...')
                
                else:
                    data = io.BytesIO(await resp.read())
                    attachments = [selfcord.File(data, f'{randomstr(randint(1, 9))}.png')]

    await asyncio.sleep(uniform(1, 5))

    # overwrite the trigger message with our own message
    await ctx.message.edit(
        content=message, 
        attachments=attachments
    )

    if edit_after:
        await asyncio.sleep(uniform(10, 20))

        # after that, delete the message
        await ctx.message.delete()

    return True


