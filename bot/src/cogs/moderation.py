

import sys
from selfcord.ext import commands
from src.config import Config
from src.utils import *


BASE_URL = "https://mksentinel.vercel.app"
API_KEY =  Config.sentinel
headers = {'X-API-Key': API_KEY}

#cogs/moderation.py
class Moderation(commands.Cog):
    def __init__(self, client):
        self.client = client

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

    async def timeout_user(self, data, reason="No reason provided", timeout_duration=60):
        if not await self.mutual_guild(data['guild'], data['member'].id):
            print(f"Timeout User (Member not found in guild): {data['member'].id}")
            return

        guild = data['guild']
        member = data['member']

        try:
            await member.timeout(timedelta(seconds=timeout_duration), reason=reason)
        except Exception as e:
            print(f"Error timing out member: {e}")
            return

        

        print(f"{data['member'].id} - {member}   {reason}")
        

    async def kick_user(self, data, reason):
        is_user_present = await self.mutual_guild(data['guild'], data['member'].id)
        if not is_user_present:
            print(f"Kick user (Failed to fetch member)")
        else:
            guild = data['guild']
            designated_channel = guild.get_channel_or_thread(Config.guilds[str(guild.id)]['ban_channel'])
            await designated_channel.send(f"<@{data['member'].id}>")
            await guild.kick(data['member'], reason=reason)
            await designated_channel.send(
                f'**Kicked**\n'
                f'UID: {data["member"].id}\n'
                f'Reason: {reason}'
            )

    async def ban_user(self, data, reason, delete_message_seconds=0, delay=0, send_panel_to_channel=False):
        is_user_present = await self.mutual_guild(data['guild'], data['member'].id)
        if not is_user_present:
            print(f"Ban user (Failed to fetch member)")
        else:
            guild = data['guild']
            designated_channel = guild.get_channel_or_thread(Config.guilds[str(guild.id)]['ban_channel'])

            from_config = Config.guilds[str(guild.id)]['ban_channel']

            
            if designated_channel is None:
                print(f"Channel not found for ID: {type(from_config)} in guild: {type(guild.id)}")
                return  # Handle the error as needed
            
            await designated_channel.send(f"<@{data['member'].id}>")
            # Check if delay is set, if so, sleep for a random time between 4 and 6 seconds
            if delay > 0:
                await asyncio.sleep(uniform(4, 6))
            
            # If data contains message, create a panel
                      
            # Commence ban
            await guild.ban(data['member'], reason=reason, delete_message_seconds=delete_message_seconds)

            # Send message details to the ban_channel
            await designated_channel.send(
                f'**Banned**\n'
                f'UID: {data["member"].id}\n'
                f'Reason: {reason}'
            )

            # Send data to the database
            await self.send_to_sentinel(data, reason)

            if data["message"]:
                await self.send_panel(data, reason, data['guild'])

                if send_panel_to_channel:
                    await asyncio.sleep(uniform(1, 2))
                    await designated_channel.send(file=selfcord.File('message_panel_small.png'))

            

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




async def setup(client):
    await client.add_cog(Moderation(client))