import os
import pusher
from dotenv import load_dotenv

load_dotenv()

# Initialize Pusher client
pusher_client = pusher.Pusher(
    app_id=os.getenv('PUSHER_APP_ID'),
    key=os.getenv('PUSHER_KEY'),
    secret=os.getenv('PUSHER_SECRET'),
    cluster=os.getenv('PUSHER_CLUSTER'),
    ssl=True
)

def trigger_event(channel, event, data):
    """
    Trigger an event on a specific channel
    
    Args:
        channel (str): The channel name
        event (str): The event name
        data (dict): The data to send with the event
    """
    try:
        pusher_client.trigger(channel, event, data)
        return True
    except Exception as e:
        print(f"Error triggering Pusher event: {e}")
        return False

def trigger_server_status():
    """
    Trigger a server status event to indicate the server is running
    """
    return trigger_event('sentinel-status', 'server-status', {
        'status': 'online',
        'timestamp': __import__('datetime').datetime.now().isoformat()
    })

def trigger_new_ban(ban_json):
    """
    Trigger a new ban event
    
    Args:
        ban_json (dict): The ban data in JSON format
    """
    return trigger_event('sentinel-status', 'new-ban', {
        'ban': ban_json
    })

def trigger_ban_removed(ban_id):
    """
    Trigger a ban removed event
    
    Args:
        ban_id (int): The ID of the removed ban
    """
    return trigger_event('sentinel-status', 'ban-removed', {
        'ban_id': ban_id
    })

def trigger_ban_updated(ban_json):
    """
    Trigger a ban updated event
    
    Args:
        ban_json (dict): The updated ban data in JSON format
    """
    return trigger_event('sentinel-status', 'ban-updated', {
        'ban': ban_json
    })

def trigger_stats_update(stats_data):
    """
    Trigger a statistics update event
    
    Args:
        stats_data (dict): The statistics data
    """
    return trigger_event('sentinel-status', 'stats-update', {
        'stats': stats_data
    })
