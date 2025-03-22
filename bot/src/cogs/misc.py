import sys
from selfcord.ext import commands
from src.utils import *

class Misc(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def echo(self, ctx, *, msg) -> None:
        """
        Echos the given message, used for testing
        """

        """
        await echo(context, message) -> nothing

        Echos the given message, used for testing

        :param ctx object: Context
        :param msg str: Message to send
        :returns None: Nothing
        """

        if ctx.message.author.id != self.client.user.id:
            return

        await sendmsg(ctx, f'> {msg}')

        

    @commands.command(aliases=['unload', 'delcog'])
    async def unloadcog(self, ctx, cog) -> None:
        """
        Unloads the specified cog
        """

        """
        await unloadcog(context, cog name) -> nothing

        Unloads the specified cog file

        :param ctx object: Context
        :param cog str: Cog name
        :returns None: Nothing
        """

        if ctx.message.author.id != self.client.user.id:
            return
        
        resp = await unload_cog(self.client, cog)
        if resp:
            await sendmsg(ctx, f'**Cog unloaded**')
        
        else:
            await sendmsg(ctx, f'**Failed to load uncog! Check console for more details**')

            if not resp: # if resp is None it means the plugin wasn't found
                resp = 'Extension not found'

            print(f'Exception occurred while unloading extension> {str(resp)}')

    

    @commands.command(aliases=['reloadcogs'])
    async def loadcogs(self, ctx) -> None:
        """
        (Re)loads all cogs
        """

        """
        await loadcogs(context) -> nothing

        Reloads all cog files

        :param ctx object: Context
        :returns None: Nothing
        """

        if ctx.message.author.id != self.client.user.id:
            return

        await load_cogs(self.client)
        await sendmsg(ctx, f'**Cogs loaded**')
    
    @commands.command(aliases=['exit', 'shutdown', 'kms', 'die'])
    async def quit(self, ctx) -> None:
        """
        Exits the bot
        """

        """
        await quit(context) -> nothing

        Closes the connection, and shuts down

        :param ctx object: Context
        :returns None: Nothing
        """

        if ctx.message.author.id != self.client.user.id:
            return
        
        await sendmsg(ctx, f'**Goodbye.**')
        await self.client.close()
        
        sys.exit()

async def setup(client):
    await client.add_cog(Misc(client))