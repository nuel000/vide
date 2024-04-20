from playwright.sync_api import sync_playwright
import re
import time
import sys

def intercept_requests(route, request):
    # Check if the request is for a font file or an image/media file
    if request.url.endswith(('.woff', '.woff2', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.bmp', '.webp','.ico')):
        print(f"Aborting request for font, image or media: {request.url}")
        route.abort()
    else:
        route.continue_()

def get_user_interaction_count(url: str) -> str:
    start_time = time.time()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.set_default_timeout(1000000)

        # Intercept requests to remove requests for custom fonts, images or media
        page.route("**/*", intercept_requests)

        page.goto(url)
        html = page.content()
        print(html)
        sys.stdout.flush()

        pattern = r'"userInteractionCount":(\d+)'

        # Search for the pattern in the content
        match = re.search(pattern, html)
        context.close()
        browser.close()


        # If a match is found, extract the userInteractionCount value
        if match:
            user_interaction_count = match.group(1)
            execution_time = time.time() - start_time  # Calculate execution time
            print(f"Execution time: {execution_time:.2f} seconds")
            sys.stdout.flush()
            return user_interaction_count
        else:
            return "Pattern not found in the content."
        
        

url = "https://twitter.com/ton_blockchain"
interaction_count = get_user_interaction_count(url)
print("User Interaction Count:", interaction_count)
sys.stdout.flush()
