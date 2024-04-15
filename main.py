
from playwright.sync_api import Playwright, sync_playwright, expect
from bs4 import BeautifulSoup
import sys

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://twitter.com/chainlink")
    html = page.content()
    s = BeautifulSoup(html,'html.parser')
    print(s.text)
    sys.stdout.flush()

    context.close()
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
