import os
import requests

url = "https://web.facebook.com/ads/library/?id=357741606925594"
splash_url = os.getenv("SPLASH_URL")

params = {
    'url': url,
    'wait': 5
}

# Define a custom session to capture requests
session = requests.Session()

# Define a custom hook function to capture requests
def capture_requests(request, *args, **kwargs):
    print("Captured URL:", request.url)
    print("Request method:", request.method)
    print("Request headers:", request.headers)
    print("Request body:", request.body)

# Register the hook function to the session
session.hooks["response"] = [capture_requests]

r = session.get(splash_url, params=params)
print(r.text)
