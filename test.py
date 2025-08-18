import requests

url = "https://app.happyrobot.ai/api/v1/calls?limit=2000&type=Outbound"
headers = {"Authorization": "Bearer 7e9a00e1ed3f5a9b04179349428c3a97"}
response = requests.get(url, headers=headers)
print(response.json())