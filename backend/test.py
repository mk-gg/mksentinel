# test_api.py
import requests

# Define the API endpoint
url = "https://mksentinel-backend.vercel.app/api/test"

# Make a GET request to the /test endpoint
response = requests.get(url)

# Check the response status code
if response.status_code == 200:
    print("Success!")
    # Print the response data (JSON)
    print(response.json())
else:
    print(f"Error: {response.status_code}")
    print(response.text)