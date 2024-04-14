import os
import requests

url = "https://web.facebook.com/ads/library/?id=357741606925594"
splash_url = os.getenv("SPLASH_URL")

params = {
    'url': url,
    'wait': 5
}

r = requests.get(splash_url, params=params)
print(r.text)
