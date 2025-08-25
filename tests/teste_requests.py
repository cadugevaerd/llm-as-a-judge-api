import requests
import json

# url_base = "http://localhost:8000"
url_base = "http://laaj.local:30080"

endpoint = "/"

response = requests.get(url_base + endpoint)
print(response.json())
