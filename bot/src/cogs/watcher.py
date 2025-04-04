import sys
from selfcord.ext import commands

from src.utils import *
from src.config import *

from src.domain_checker import URLProcessor

from rich.console import Console
from rich.progress import Progress

server_bots = {
    396548639641567232,  # Mavis Market Bot (new)
    1110593454012104745, # Mavis Market Bot
    823695836319055883,  # AxieBot 
    1230221894221824222, # Axie.Bot [App]
    1217477415757025444, # EndlessHerald [Axie Infinity]
}

ignore_domains = {
    'x.com', 
    'tenor.com',
    'cdn.discordapp.com',
    'tama.meme',
    'media.discordapp.net',
    'cdn.discordapp.com',
    'app.axieinfinity.com'
}
url_processor = URLProcessor(ignore_domains)

BASE_URL = "https://mksentinel.vercel.app"
API_KEY =  Config.sentinel
headers = {'X-API-Key': API_KEY}
JOIN_AGE_ACCOUNT = 50

def contains_any_domain(text: str, ignore_domains: set) -> bool:
    """
    Checks if a string contains any of the domains in the provided set.

    Args:
        text: The string to check.
        ignore_domains: A set of domains to look for.

    Returns:
        True if the string contains any of the domains, False otherwise.
    """
    for domain in ignore_domains:
        if domain in text:
            return True
    return False


def filter_duplicates(container):
    seen_ids = set()
    unique_entries = []

    for entry in container:
        entry_id = entry[0]  # Assuming the ID is the first element in each sublist
        # Check if the ID is not in seen_ids
        if entry_id not in seen_ids:
            seen_ids.add(entry_id)
            # Append the entry, regardless of whether the reason is present or not
            unique_entries.append(entry)


    return unique_entries

def is_scam_server(name):
    if name is None:
        return False
    scam_keywords = {"support", "tickets","support-tickets", "support server", "ticket support", "helpdesk center", "create ticket", "helpdesk", "help desk", "help center", "support ticket", "ticket tool", "ticket", "server support", "customer support", "technical support", "help-center", "help", "help-centre", "resolution"}
    return any(keyword.lower() in name.lower() for keyword in scam_keywords)

def is_discord_url(url):
    parsed_url = urllib.parse.urlparse(str(url))  # Convert url to string
    domain = parsed_url.netloc
    return domain.endswith(("discord.com", "discord.gg"))

def get_guild_name(url):
    # Extract the invite code from the URL using a regular expression
    match = re.search(r'https?://discord(?:\.com/invite|\.gg)/([a-zA-Z0-9-]+)', url)
    if match:
        invite_code = match.group(1)
        try:
            response = requests.get(f"https://discord.com/api/v8/invites/{invite_code}") 
            response.raise_for_status()  # Raise an exception for a failed request

            data = response.json()


            if "guild" in data:
                guild_name = data["guild"]["name"]
                return guild_name
 
            
            
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except requests.exceptions.RequestException as err:
            print(f"Error occurred: {err}")
    else:
        print("Invalid Discord invite link")


#cogs/watcher.py
class Watcher(commands.Cog):
    def __init__(self, client):
        self.client = client

        self.main_queue = asyncio.Queue()
        self.user_locks = {}
        self.background_task = asyncio.create_task(self.process_queue())

    
    async def process_queue(self):
        while True:
            data = await self.main_queue.get()
            
            user_id = data['user_id']

            async with self.user_locks.setdefault(user_id, asyncio.Lock()):
                
                event_handlers = {
                    'message': self.handle_message_event,
                    'update': self.handle_update_event,
                    'join': self.handle_join_event,
                }

                if data['event'] in event_handlers:
                    await event_handlers[data['event']](data)
            
            self.main_queue.task_done()

    async def is_scam_attempt(self, data):
        try:
            has_multiple_lines = has_multiple_new_lines(data['message'])
            message = data['message']
            if has_multiple_lines:
                message = combine_lines(data['message'])
            # print(f"{message}")
            normalized_message = translate_confusable_characters(message)
            processed_final_link = url_processor.process_url(normalized_message)
            if processed_final_link:
                link = contains_any_domain(processed_final_link, ignore_domains)
                if not link:
                    processed_final_link= clean_normalize_url_ai(processed_final_link)
                    print(f"Final Link: {processed_final_link}")
            
            if is_discord_url(processed_final_link):
                guild_name = get_guild_name(processed_final_link)
                if guild_name:
                    if is_scam_server(guild_name):
                        return True
                        # await data['message_obj'].add_reaction('⚠️')
                        # create_panel(processed_final_link, "Scam Server", guild_name,  data['message'], data['member'])
                        # moderation_cog = self.client.get_cog('Moderation')
                        # if moderation_cog:
                            # await moderation_cog.ban_user(data, reason="Scam Attempt", delay=0, delete_message_seconds=3600)
             
            return False
        except Exception as e:
            print(e)

    async def handle_message_event(self, data):
        
        await printlog(data, data['event'])
        pass
        # try:
        #     has_multiple_lines = has_multiple_new_lines(data['message'])
        #     message = data['message']
        #     if has_multiple_lines:
        #         message = combine_lines(data['message'])
        #     # print(f"{message}")
        #     normalized_message = translate_confusable_characters(message)
        #     processed_final_link = url_processor.process_url(normalized_message)
        #     if processed_final_link:
        #         link = contains_any_domain(processed_final_link, ignore_domains)
        #         if not link:
        #             processed_final_link= clean_normalize_url_ai(processed_final_link)
        #             print(f"Final Link: {processed_final_link}")
            

            

        #     if is_discord_url(processed_final_link):
        #         guild_name = get_guild_name(processed_final_link)
        #         if guild_name:
        #             if is_scam_server(guild_name):
                        
        #                 await data['message_obj'].add_reaction('⚠️')
        #                 create_panel(processed_final_link, "Scam Server", guild_name,  data['message'], data['member'])
        #                 moderation_cog = self.client.get_cog('Moderation')
        #                 if moderation_cog:
        #                     await moderation_cog.ban_user(data, reason="Scam Attempt", delay=0, delete_message_seconds=3600)
             
            
        # except Exception as e:
        #     print(e)

    async def handle_update_event(self, data):
        print(f'Called handle_update_event')

    async def handle_join_event(self, data):
        print(f'Called handle_join_event')

    
    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignore DMs
        if message.guild is None:
            return  
        # Ignore out of scope guilds
        if str(message.guild.id) not in Config.guilds:
            return
        # Ignore Server bots
        if message.author.id in server_bots:
            return
        try:
        
            is_within_date = False  # Default value
            joined_at_str = message.author.joined_at.strftime("%Y-%m-%d %H:%M:%S%z")
            is_within_date = check_date(joined_at_str, JOIN_AGE_ACCOUNT)
        except Exception as e:
            pass
        # Ignore messages from users who joined the server greater than JOIN_AGE_ACCOUNT
        if not is_within_date:
            return
        try:
            if message.type == selfcord.MessageType.auto_moderation_action:
                for embed in message.embeds:
                    embed_dict = embed.to_dict()
                    sent_message = embed_dict.get('description', '')
            else:
                sent_message = message.content
            
            data = {
                'event': 'message',
                'member': message.author,
                'user_id': message.author.id,
                'guild': message.guild,
                'message': sent_message,
                'message_obj': message
            }

            await self.main_queue.put(data)
        except Exception as e:
            print(e)

    
    async def send_to_sentinel(self, data, reason):
        """
        Send ban data to the sentinel service asynchronously.
        
        Args:
            data (dict): Contains member and guild information
            reason (str): The reason for the ban
        
        Returns:
            dict|None: Response from sentinel service or None if request fails
        """
        member = data['member']
        guild = data['guild']
        # More thorough message validation
        message = data.get('message')
        if message is None or message == 'None' or not message:
            message = ''
        
        
        try:
            member_data = {
                'memberId': str(member.id),
                'username': member.name,
                'displayName': member.display_name,
                'serverId': str(guild.id),
                'serverName': str(guild),
                'capturedMessage': message,
                'reason': reason
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f'{BASE_URL}/api/ban',
                    headers=headers,
                    json=member_data
                ) as response:
                    if response.status == 201:
                        print(f"Successfully sent user {member_data['username']} data to Sentinel")
                        return await response.json()
                    else:
                        print(f"Failed to create ban. Status code: {response.status}")
                        error_text = await response.text()
                        print(f"Error: {error_text}")
                        return None
                        
        except aiohttp.ClientError as e:
            print(f"Error making request: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None
    
    async def mutual_guild(self, guild, member_id):
        """
        Check if a user is in the same server as the bot.

        Args:
            guild (discord.Guild): The guild object to check for the user.
            member_id (int): The ID of the user to check.

        Returns:
            bool: True if the user is in the same server as the bot, False otherwise.

        Raises:
            discord.errors.NotFound: If the user is not found in the guild.
        """
        try:
            resp = await guild.fetch_member(member_id)
            return True
        except selfcord.errors.NotFound:
            return False
    
    async def send_panel(self, data, reason, designated_guild):
        
        LOGGING_GUILD_ID = 438327036205858818
        CHANNEL_MAPPINGS = {
            "Ronin Network": 1301454090554834974,
            "default": 1301454060787863593  # This is for Axie Infinity and any other guild
        }
        member = data['member']
        guild = self.client.get_guild(LOGGING_GUILD_ID)
        

        
        avatar = member.avatar.url if member.avatar and member.avatar.url else ""
        
        try:
            small_panel = create_message_panel(
                name=member.name,
                uid=member.id,
                reason=reason,
                message=data["message"],
                avatar_url=avatar,
                show_title=False,
                max_chars=1000,  # Truncate after 100 chars
                scale=0.8  # Half size
            )
            small_panel.save("message_panel_small.png")
            print(f"[green]Done creating panel[/]")
        except Exception as e:
            print(f"Error creating panel: {str(e)}")
            return

        try:
            channel_id = CHANNEL_MAPPINGS.get(designated_guild.name, CHANNEL_MAPPINGS["default"])
            channel = guild.get_channel_or_thread(channel_id)
            await channel.send(file=selfcord.File('message_panel_small.png'))
        except Exception as e:
            print(f"Error sending message: {e}")

    async def ban_user(self, data, reason, delete_message_seconds=0, delay=0, send_panel_to_channel=False):
        is_user_present = await self.mutual_guild(data['guild'], data['member'].id)
        if is_user_present:
            try:
                guild = data['guild']
                #user = guild.fetch_member(data['member'].id)
            except selfcord.NotFound as e:
                print(f"Ban User (Failed to fetch member): {e}")

            
   
           
            # print(f"{time_format} {guild_format} [{event_msg}] {data['member'].id} - {data['member']}   {reason}")
            await printlog(data, data['event'], reason)
            channel = guild.get_channel_or_thread(Config.guilds[str(guild.id)]['ban_channel'])
            await channel.send(f"<@{data['member'].id}>")

            if delay > 0:
                await asyncio.sleep(uniform(4, 6))

            

            

            await guild.ban(data['member'], reason=reason, delete_message_seconds=delete_message_seconds)
            await channel.send(
                f'**Banned**\n'
                f'UID: {data["member"].id}\n'
                f'Reason: {reason}'
            )
            if data["message"]:
                await self.send_panel(data, reason, data['guild'])

                if send_panel_to_channel:
                    await asyncio.sleep(uniform(1, 2))
                    await channel.send(file=selfcord.File('message_panel_small.png'))
                    
            await self.send_to_sentinel(data, reason)
            
                

    
            



    @commands.command(aliases=['check'])
    async def check_users(self, ctx):
        if ctx.message.author.id != self.client.user.id:
            return
        
        # Configuration
 # Replace with your actual API key
        GUILD_IDS = {
            930892666705694800: "Ronin Network",
            410537146672349205: "Axie Infinity"
        }
        
        # Fetch banned users
        unique_member_ids = await self.fetch_banned_users()
        if not unique_member_ids:
            await ctx.send("Failed to retrieve banned users or no bans found.")
            return
            
        # Check each guild for banned members
        for guild_id, guild_name in GUILD_IDS.items():
            await self.check_guild_for_banned_members(guild_id, guild_name, unique_member_ids)

    async def fetch_banned_users(self):
        """Fetch banned user IDs from the API"""
   
        
        try:
            response = requests.get(
                'https://mksentinel.vercel.app/api/bans',
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()
            
            # Check if 'bans' key exists in data
            if 'bans' not in data:
                print("No bans found in the response.")
                return []
                
            # Extract and deduplicate member IDs
            member_ids = [int(ban['memberId']) for ban in data['bans']]
            return list(set(member_ids))
            
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            print(f"Response content: {e.response.text if hasattr(e, 'response') else 'No response'}")
            return []

    async def check_guild_for_banned_members(self, guild_id, guild_name, banned_ids):
        """Check if any banned users are present in the specified guild"""
        guild = self.client.get_guild(guild_id)
        if not guild:
            print(f"Could not find guild with ID {guild_id}")
            return
            
        guild_member_ids = [member.id for member in guild.members]
        present_member_ids = [member_id for member_id in banned_ids if member_id in guild_member_ids]
        
        if present_member_ids:
            print(f'Members present in the {guild_name} guild: {present_member_ids}')
        else:
            print(f'No banned members are present in the {guild_name} guild.')

    @commands.command(aliases=['purge'])
    async def purge_data(self, ctx):
        if ctx.message.author.id != self.client.user.id:
            return
        
    
        



        container = [

            [1349600801516945468, 'Scam Bio Link', ''],
            [1356694338041679933, 'Scam Bio Link', ''],
            [1331598769304895580, 'User banned from Axie Infinity for Scam Attempt', r'🎫[**Use the official link to contact the support team here for assistance!!**]<https:/%64%69%73%63%6f%72%64%2e%67%67/%62%74%4D%54%62%75%32%46%4B%32>'],
            [1348642413702549535, 'User banned from Axie Infinity for Scam Attempt', r'Reach out to admin for help here👇👇**<https:/%64%69%73%63%6f%72%64%2e%67%67/%7A%50%34%41%71%64%41%42%41%57>**'],
            [1334202682189025351, 'User banned from Axie Infinity for Scam Attempt', r'Kindly Contact The Support Center⬇️ For Assistancediscord.com/invite\TVTURF2Dek'],

            [1089340754175991960, 'User banned from Ronin Network for Scam Attempt', r'<https:/%64%69%73%63%6F%72%64%2E%67%67/%4A%33%79%4A%58%64%6A%4B%52%61>to the team'],
            [1185730314249703525, 'User banned from Ronin Network for Scam Attempt', r'**[CREATE A TlCKET🎫]:**👇<https:/%64%69%73%63%6f%72%64%2e%67%67/%55%4b%52%68%77%63%59%45%59%36> <@1354921261339246763>'],
            [1339729916941308004, 'User banned from Ronin Network for Scam Attempt', r'REACH OUT TO AN ADMIN FOR MORE ASSISTANCEdiscordapp.com/invite\Kb2sqgewXJ <@1071006504850821262>'],
            [1339549011186679850, 'User banned from Ronin Network for Scam Attempt', r'Write your issues here for prompt assistance👇🏽https://discord.gg/eWnRTCes'],
            [1345662833685430273, 'User banned from Ronin Network for Scam Attempt', r'Get it sorted ⬇️⬇️** <https:/%64%69%73%63%6f%72%64%2e%67%67/%37%72%32%45%56%62%42%58%56%46>**'],
            [566487433391243273, 'User banned from Ronin Network for Scam Attempt', r'<https:/%64%69%73%63%6f%72%64%2e%67%67/%59%74%38%6b%4d%78%45%51%4e%45> relay query to team'],
            [936744039699587092, 'User banned from Ronin Network for Scam Attempt', r'ASK ADMINS⬇️ ⬇️ <https:/%64%69%73%63%6f%72%64%2e%67%67/%32%61%45%32%7a%64%73%33>'],

            [1340373728730808331, 'User banned from Ronin Network for Scam Attempt', r'👇👇👇 *SUBMIT QUERY*<https:/%64%69%73%63%6f%72%64%2e%67%67/%5a%36%71%68%76%5a%66%42%78%53>'],
            [1330915964086386723, 'User banned from Ronin Network for Scam Attempt', r'Refer this question to the Team 🎫 <https:/%64%69%73%63%6F%72%64%2E%67%67/%73%4A%67%67%4A%63%70%72%38%45> <@268155334802014208>'],
            
            [1199116626113593356, 'Scam Bio Link', ''],
            [1222012542809931786, 'Scam Bio Link', ''],
            [1220040770430439434, 'Scam Bio Link', ''],
            [1218539315928371251, 'Scam Bio Link', ''],
            [1217839557219713038, 'Scam Bio Link', ''],
            [1215920671314411563, 'Scam Bio Link', ''],
            [1218901602048675930, 'Scam Bio Link', ''],
            [1217880881595678905, 'Scam Bio Link', ''],

            [1072373597785575454, 'Scam Bio Link', ''],





      


            # [1329362079420780607, 'Scam / Impersonation'],
            # [1194058979647701097, 'Scam Attempt'],
            
        
            [1346332139402297355, 'Bot Account', '']

        ]
        
        data = filter_duplicates(container)
        print("Done filtering..")
        # Hash list
        #data = filter_data(fillet)
    
        
        
        # Ban phase
        print(f'[#f07443]Commencing purge')
        progress_data = 0
        with Progress() as progress: 
            task1 = progress.add_task("[red]Banning...", total=len(data))

            # Iterate the filtered data
            for item in data:
                progress_data = progress_data + 1

                member_id = item[0]
                reason = item[1]
                sent_message = item[2]
                try:
                    member = await self.client.fetch_user_profile(member_id, with_mutual_guilds=True)
                    mutual_guilds = member.mutual_guilds
                    # Check if user is still in the guild
                    if mutual_guilds:
                        for mutual_guild in member.mutual_guilds:
                            guild_id = mutual_guild.guild.id
                            if str(guild_id) in Config.guilds:
                                """
                                Get the corresponding server and channel to ban the user
                                """
                                guild = self.client.get_guild(guild_id)
                                member_data = {
                                    'user_id': member_id,
                                    'guild': guild,
                                    'member': member,
                                    'message': sent_message,
                                    'event': 'ban'
                                }
                                #print(f"Name: {member} Guild: {guild}  Channel: {channel}")
                                moderation_cog = self.client.get_cog('Moderation')
                                await moderation_cog.ban_user(member_data, reason=reason, send_panel_to_channel=True, delay=6, delete_message_seconds=3600)
                                # await self.ban_user(member_data, reason, delete_message_seconds=3000, delay=6, send_panel_to_channel=True)
                    else:
                        print("The user has no mutual guilds with the bot.")
                    # Access and process mutual guilds here
                except selfcord.Forbidden:
                    pass
                except Exception as e:
                    print(f"An error occurred: {e}")

            


                
                progress.update(task1, advance=1)
            

        print(f'[#90c24a]Purging complete!')

    

async def setup(client):
    await client.add_cog(Watcher(client))