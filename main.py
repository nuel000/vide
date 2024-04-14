import requests
import sys

def run():
    url = "https://web.facebook.com/ads/library/?id=357741606925594"
    splash_url = "http://splash:8050/render.html"

    params = {
        'url': url,
        'wait': 5
    }

    r = requests.get(splash_url, params=params)
    response_text = r.text

    print(response_text)
    sys.stdout.flush()
run()
