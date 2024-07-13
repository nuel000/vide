
import sys
from playwright.sync_api import Playwright, sync_playwright, expect
import time
from bs4 import BeautifulSoup


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://www.vinted.co.uk/catalog?search_text=&size_ids\\[]=207&size_ids[]=208&size_ids[]=209&size_ids[]=210&size_ids[]=211&size_ids[]=212&size_ids[]=213&brand_ids[]=53&brand_ids[]=14&brand_ids[]=162&brand_ids[]=21099&brand_ids[]=345&brand_ids[]=245062&brand_ids[]=359177&brand_ids[]=484362&brand_ids[]=313669&brand_ids[]=8715&brand_ids[]=378906&brand_ids[]=140618&brand_ids[]=1798422&brand_ids[]=597509&brand_ids[]=1065021&brand_ids[]=57144&brand_ids[]=345731&brand_ids[]=269830&brand_ids[]=99164&brand_ids[]=73458&brand_ids[]=719079&brand_ids[]=670432&brand_ids[]=299684&brand_ids[]=1985410&brand_ids[]=311812&brand_ids[]=291429&brand_ids[]=1037965&brand_ids[]=472855&brand_ids[]=511110&brand_ids[]=299838&brand_ids[]=8139&brand_ids[]=401801&brand_ids[]=3063&brand_ids[]=1412112&brand_ids[]=725037&brand_ids[]=164166&brand_ids[]=190014&brand_ids[]=46923&brand_ids[]=506331&brand_ids[]=13727&brand_ids[]=345562&brand_ids[]=335419&brand_ids[]=318349&brand_ids[]=276609&search_id=14979857318&order=newest_first")
    page.get_by_test_id("domain-select-modal-close-button").click()
    print('Clicked on close button')
    sys.stdout.flush()
    page.get_by_role("button", name="Accept all").click()
    print('Clicked on accept button')
    sys.stdout.flush()
    time.sleep(5)
    
    s = BeautifulSoup(page.content(),'html.parser')
    cards = s.find('div',class_='feed-grid')
    links = cards.find_all('a')
    for i in links:
        print(i.get('href'))
        sys.stdout.flush()
