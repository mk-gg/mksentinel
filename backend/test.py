# test_api.py
import json
from dotenv import load_dotenv, dotenv_values
import requests
import os
load_dotenv(verbose=True)

# Define the API endpoint
WEBSITE_URL = "https://mksentinel.vercel.app"
API_KEY = os.environ.get('SENTINEL_SECRET')
headers = {'X-API-Key': API_KEY}

def test_auth_decorator():
    # Test without credentials
    no_auth_response = requests.get(f'{WEBSITE_URL}/api/members')
    print( no_auth_response.status_code == 401, "Should require authentication")

    # Test with API key
    api_key_headers = {'X-API-Key': API_KEY}
    api_key_response = requests.get(f'{WEBSITE_URL}/api/members', headers=api_key_headers)
    print( api_key_response.status_code == 200, "API key should grant access")

def get_test():
    # Make a GET request to the /test endpoint
    response = requests.get(f'{WEBSITE_URL}/config-test')

    # Check the response status code
    if response.status_code == 200:
        print("Success!")
        # Print the response data (JSON)
        print(response.json())
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

def get_test2():
    # Make a GET request to the /test endpoint
    response = requests.get(f'{WEBSITE_URL}/vercel-env-check')

    # Check the response status code
    if response.status_code == 200:
        print("Success!")
        # Print the response data (JSON)
        print(response.json())
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

def get_test_api():
    # Make a GET request to the /test endpoint
    response = requests.get(f'{WEBSITE_URL}/some-endpoint')

    # Check the response status code
    if response.status_code == 200:
        print("Success!")
        # Print the response data (JSON)
        print(response.json())
    else:
        print(f"Error: {response.status_code}")
        print(response.text)



member_data = {
    'memberId': '1320481335349084252',
    'username': 'justinfletcher06',
    'displayName': 'Support Administrator',
    'serverId': '410537146672349205',
    'serverName': 'Axie Infinity',
    'capturedMessage': '',
    'reason': 'Fake Support'
}

def get_members(): 
    try:
    
        response = requests.get(
            f'{WEBSITE_URL}/api/bans/statistics'
        )
        response.raise_for_status()  # Raises an HTTPError for bad responses
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        print(f"Response content: {e.response.text if hasattr(e, 'response') else 'No response'}")
        return None

def add_ban(member_data=member_data):
    try:

        response = requests.post(
            'https://mksentinel-backend.vercel.app/ban',
            headers=headers,
            json=member_data
        )

        if response.status_code == 201:
            print(f"Successfully banned user {member_data['username']}")
            return response.json()
        else:
            print(f"Failed to create ban. Status code: {response.status_code}")
            print(f"Error: {response.json()}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        return None


def get_ban_id():
    try:
        member_id = '1241650567030378527'
        url = f'{WEBSITE_URL}/ban/{2}'
        response = requests.get(
            url,
            headers=headers
        )

        # GET requests return 200 for success, not 201
        if response.status_code == 200:
            print(f"Successfully retrieved ban for member {member_id}")
            return response.json()
        else:
            print(f"Failed to get ban. Status code: {response.status_code}")
            print(f"Error: {response.json()}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        return None

def test_env():
    env = dotenv_values(".env")
    key =  API_KEY
    print(env)
    print(key)


# data = test_env()
# data = test_auth_decorator()
data = get_test()
data = get_test2()
# data = some_endpoint()
# data = get_test_api()
# data = get_members()



# print(json.dumps(get_test(), indent=2))
# print(API_KEY)