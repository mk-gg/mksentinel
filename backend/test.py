# test_api.py
import requests
import os


# Define the API endpoint
url = "https://mksentinel-backend.vercel.app/test"
API_KEY = os.environ.get('API_KEY')
headers = {'X-API-Key': API_KEY}

def get_test():
    # Make a GET request to the /test endpoint
    response = requests.get(f'{url}')

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
    'serverId': 410537146672349205,
    'serverName': 'Axie Infinity',
    'capturedMessage': '',
    'reason': 'Fake Support'
}

def get_members(): 
    response = requests.get(
        'https://mksentinel-backend.vercel.app/members',
        headers=headers
    )
    if response.status_code != 200:
        print(f"Error: {response.status_code}", response.json())
        return None
    return response.json()

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

data = get_test()
# print(API_KEY)