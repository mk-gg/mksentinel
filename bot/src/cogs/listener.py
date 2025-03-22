import sys
from selfcord.ext import commands
from src.config import Config
from src.utils import *

server_bots = {
    396548639641567232,  # Mavis Market Bot (new)
    1110593454012104745, # Mavis Market Bot
    823695836319055883,  # AxieBot 
    1230221894221824222, # Axie.Bot [App]
    1217477415757025444, # EndlessHerald [Axie Infinity]
}

JOIN_AGE_ACCOUNT = 50

#cogs/listener.py
class Listener(commands.Cog):
    def __init__(self, client):
        self.client = client
        # Queue
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
        
    # Listen to events
    @commands.Cog.listener()
    async def on_member_join(self, member):
        if str(member.guild.id) not in Config.guilds:
            return
        try:
            member_profile = await member.profile(with_mutual_guilds=False, with_mutual_friends_count=False, with_mutual_friends=False)
        except Exception as e:
            print(f"Failed to get member_profile on member_join: {e}")
        if member_profile and member_profile.display_bio:
            print(f"[#FDB7EA][{member.guild}][/] Bio of {member}:  {member_profile.display_bio}")



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


    # Handle events
    async def handle_update_event(self, data):
        print(f'Called handle_update_event')

    async def handle_join_event(self, data):
        print(f'Called handle_join_event')
    
    async def handle_message_event(self, data):
        scam_message = self.client.get_cog('MessageParse')
        if scam_message:
            # Check using the method from MessageParse
            sent_message = data['message']
            is_scam_message = await scam_message.is_similar(sent_message)
            if is_scam_message:
                try:
                    await data['message_obj'].add_reaction('⚠️')
                except Exception as e:
                    print(e)
                data['reason'] = "Scam Attempt"
                await self.ban_user_service(data)
    
    async def ban_user_service(self, data):
        moderation_cog = self.client.get_cog('Moderation')
        if moderation_cog:
            await moderation_cog.ban_user(data, reason=data['reason'], send_panel_to_channel=True, delete_message_seconds=3600)

        
       

        

    


async def setup(client):
    await client.add_cog(Listener(client))