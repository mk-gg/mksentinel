import sys


from src.config import *
from src.utils import *



load_config()



client = commands.Bot(
    command_prefix = Config.prefix,
    caseinsensitive = True,
    self_bot = True
)

@client.event
async def on_connect() -> None:
    """
    on_connect() -> nothing
 
    Runs when Ribbit connects to the Discord gateway

    :returns None: Nothing
    """

@client.event
async def on_command_error(ctx, error) -> None:
    """ 
    on_command_error(context, error) -> nothing
    
    Error handler

    :param ctx object: Context
    :param error object: Exception
    :returns None: Nothing
    """
    orig_error = getattr(
        error,  
        'original',
        error
    )

    error = str(error).rstrip()
    if isinstance(orig_error, commands.CommandNotFound):
        print(f'Command not recognized> {error}')
        await sendmsg(ctx, f'**Command not recognized**: `{error}`')
    
    elif isinstance(orig_error, (commands.MissingRole, commands.MissingAnyRole)):
        print(f'Missing role(s)> {error}')
        await sendmsg(ctx, f'**Missing role(s)**: `{error}`')
    
    elif isinstance(orig_error, commands.CommandOnCooldown):
        print(f'Command is on cooldown> {error}')
        await sendmsg(ctx, f'**Command is on cooldown**: `{error}`\n**Seconds until cooldown is finished**: `{round(orig_error.retry_after, 2)}`')
    
    else:
        print(f'Error appeared> {str(error)}')
        await sendmsg(ctx, f'**Error**: `{str(error)}`')

    await asyncio.sleep(uniform(1, 2))

    # sometimes the message already gets deleted by the user, so we wrap    this up
    # incase it does happen (else code will error out)
    try:
        await ctx.message.delete()
    except Exception:
        pass


@client.event
async def on_ready() -> None:
    """
    on_ready() -> nothing

    Runs when Ribbit is fully ready

    :returns None: Nothing
    """

    #clear()

    if not client.user:
        sys.exit('User not logged in!')

    print('''
        ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⠿⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
        ⣿⣿⣿⣿⣿⣿⣿⠛⢩⣴⣶⣶⣶⣌⠙⠫⠛⢋⣭⣤⣤⣤⣤⡙⣿⣿⣿⣿⣿⣿
        ⣿⣿⣿⣿⣿⡟⢡⣾⣿⠿⣛⣛⣛⣛⣛⡳⠆⢻⣿⣿⣿⠿⠿⠷⡌⠻⣿⣿⣿⣿
        ⣿⣿⣿⣿⠏⣰⣿⣿⣴⣿⣿⣿⡿⠟⠛⠛⠒⠄⢶⣶⣶⣾⡿⠶⠒⠲⠌⢻⣿⣿
        ⣿⣿⠏⣡⢨⣝⡻⠿⣿⢛⣩⡵⠞⡫⠭⠭⣭⠭⠤⠈⠭⠒⣒⠩⠭⠭⣍⠒⠈⠛
        ⡿⢁⣾⣿⣸⣿⣿⣷⣬⡉⠁⠄⠁⠄⠄⠄⠄⠄⠄⠄⣶⠄⠄⠄⠄⠄⠄⠄⠄⢀
        ⢡⣾⣿⣿⣿⣿⣿⣿⣿⣧⡀⠄⠄⠄⠄⠄⠄⠄⢀⣠⣿⣦⣤⣀⣀⣀⣀⠄⣤⣾
        ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣶⣶⡶⢇⣰⣿⣿⣟⠿⠿⠿⠿⠟⠁⣾⣿⣿
        ⣿⣿⣿⣿⣿⣿⣿⡟⢛⡛⠿⠿⣿⣧⣶⣶⣿⣿⣿⣿⣿⣷⣼⣿⣿⣿⣧⠸⣿⣿
        ⠘⢿⣿⣿⣿⣿⣿⡇⢿⡿⠿⠦⣤⣈⣙⡛⠿⠿⠿⣿⣿⣿⣿⠿⠿⠟⠛⡀⢻⣿
        ⠄⠄⠉⠻⢿⣿⣿⣷⣬⣙⠳⠶⢶⣤⣍⣙⡛⠓⠒⠶⠶⠶⠶⠖⢒⣛⣛⠁⣾⣿
        ⠄⠄⠄⠄⠄⠈⠛⠛⠿⠿⣿⣷⣤⣤⣈⣉⣛⣛⣛⡛⠛⠛⠿⠿⠿⠟⢋⣼⣿⣿
        ⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠈⠉⠉⣻⣿⣿⣿⣿⡿⠿⠛⠃⠄⠙⠛⠿⢿⣿
        ⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⢬⣭⣭⡶⠖⣢⣦⣀⠄⠄⠄⠄⢀⣤⣾⣿
        ⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⢰⣶⣶⣶⣾⣿⣿⣿⣿⣷⡄⠄⢠⣾⣿⣿⣿    
        ''')
    
    print(f'[#2eb5c7]Logged in as "{client.user.global_name}" (username:{client.user}) (id: {client.user.id})')
    print(f'> Extensions/cogs loaded: {str(len(client.extensions))}')
    print(f'> Started at: {str(get_time_now())}')
    print(f'> Connected at: {str(get_time_now())}')
    print(f'> Ping: {str(round(client.latency * 1000))} ms\n')

if __name__ == '__main__':
    #.clear()
    try:    
        asyncio.run(load_cogs(client))
        client.run(Config.token)
    
    except KeyboardInterrupt:
        pass

    except Exception as e:
        asyncio.run(client.close())
        print(f'Exception while connecting: {str(e).rstrip()}')

        

    save_config()
    sys.exit('\nClosing.')