import re
import json
import requests
import subprocess
import pandas as pd
from bs4 import BeautifulSoup
import pandas as pd
import gspread
from googleapiclient.discovery import build
from google.oauth2 import service_account
from gspread_dataframe import set_with_dataframe
from google.oauth2.service_account import Credentials
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import html
from datetime import datetime
import sys
from playwright.sync_api import Playwright, sync_playwright, expect
import time
from bs4 import BeautifulSoup
import json
import pandas as pd
from datetime import datetime

start_time = datetime.now()
f_start_time = start_time.strftime('%Y-%m-%d %H:%M:%S')


headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'}

#------------------------------------------------------------------------------------------------------------------------------------------
# SCRAPING www.ballou976.com

scopes = ['https://www.googleapis.com/auth/spreadsheets',
          'https://www.googleapis.com/auth/drive']

credentials = Credentials.from_service_account_file('lambert_2.json', scopes=scopes)
gc = gspread.authorize(credentials)

gauth = GoogleAuth()
drive = GoogleDrive(gauth)

def scrape_page(url):
    response = requests.get(url,headers = headers)
    s = BeautifulSoup(response.content, 'html.parser')
    all_products = s.find('table',class_='table table-borderless m-0').find_all('tr')
    all_links = []
    for i in all_products:
      links = i.find_all('a')
      all_links.append(links)
    urls = []
    for html_list in all_links:
        soup = BeautifulSoup(''.join([str(tag) for tag in html_list]), 'html.parser')
        for tag in soup.find_all('a'):
            urls.append('https://www.ballou976.com'+tag.get('href'))
    urls =list(set(urls))


    def extract_reference_and_title(text):
      # Define the regex pattern to match the reference number and title
      pattern = r"\[(.*?)\]\s*(.*)"

      # Use re.match to find matches
      match = re.match(pattern, text)

      if match:
          reference = match.group(1)  # The reference number
          title = match.group(2)  # The title
          return reference, title
      else:
          return None, None

    data = []

    for i in urls:
        r2 = requests.get(i, headers=headers)
        s2 = BeautifulSoup(r2.content, 'html.parser')

        # Description
        try:
          description = s2.find('p', class_='text-muted my-2').text.replace('\n', ' ').replace('\r', ' ').strip()
        except:
          description = f"No description for {i}"
        try:
            section = s2.find('section', class_='container py-4 oe_website_sale discount')
            product_data = section['data-product-tracking-info']
        except:
            section = s2.find('section', class_='container py-4 oe_website_sale')
            product_data = section['data-product-tracking-info']

        product_details = json.loads(product_data)
        item_id = product_details['item_id']
        item_description = product_details['item_name'].replace('\n', ' ').replace('\r', ' ').strip()
        reference, title = extract_reference_and_title(item_description)
        category = product_details['item_category'].replace('\n', ' ').replace('\r', ' ').strip()
        old_price = int(product_details['price'])

        try:
            current_price = s2.find('span', class_='oe_price').text.split(',')[0].replace('\n', ' ').replace('\r', ' ').strip()
        except:
            current_price = old_price

        # Append the data to the list
        data.append([item_id, title, reference, category, current_price, old_price, description])
    # Find the next page link
    next_page = s.find('div',class_='products_pager form-inline justify-content-center py-3').find_all('li')[-1]
    next_page_url = None
    if next_page:
        next_page_url = next_page.find('a').get('href')

    return data, next_page_url

def scrape_all_pages(start_url):
    all_data = []
    current_url = start_url

    while current_url:
        print(f"Scraping: {current_url}")
        sys.stdout.flush()
        data, next_page_url = scrape_page(current_url)
        all_data.append(data)

        if next_page_url:
            current_url = "https://www.ballou976.com" + next_page_url  # Modify as necessary
        else:
            current_url = None

    return all_data

start_url = "https://www.ballou976.com/shop"  # Starting URL
all_scraped_data = scrape_all_pages(start_url)

flattened_data = [item for sublist in all_scraped_data for item in sublist]

# Define the column names
columns = ['item_id', 'title', 'reference', 'category', 'current_price', 'old_price', 'description']

# Create a DataFrame
df = pd.DataFrame(flattened_data, columns=columns)

# open a google sheet
gs = gc.open_by_key('1Fl00gau4qbcNZMZUQXCkpfXneJSe3ox1wtqL-Shq3Dc')
# select a work sheet from its name
worksheet1 = gs.worksheet('www.ballou976.com')
worksheet1.clear()
set_with_dataframe(worksheet=worksheet1, dataframe=df, include_index=False,
include_column_header=True, resize=True)
print('Google Sheet updated with Df for www.ballou976.com')
sys.stdout.flush()

#-----------------------------------------------------------------------------------------------------------------------------------
# SCRAPING www.kalo.yt

r_first = requests.get('https://kalo.yt/fr/10-gros-electromenager',headers = headers)
s_first = BeautifulSoup(r_first.content,'html.parser')
categories = s_first.find('div',class_='sidebar col-xs-12 col-sm-12 col-md-4 col-lg-3')
lis = categories.find('ul',class_='category-sub-menu').find_all('li')
all_links = [x.find('a') for x in lis]
sub_links = [x.find('a',class_='category-sub-link') for x in lis]
categories_urls = [x.get('href') for x in all_links if x not in sub_links]

def scrape_page(url):
  products_list = []
  r_k = requests.get(url,headers = headers)
  s_k = BeautifulSoup(r_k.content, 'html.parser')
  products = s_k.find_all('article',class_='product-miniature js-product-miniature')
  links = [x.find('a').get('href') for x in products]

  for link in links:
    r2 = requests.get(link, headers=headers)
    s2 = BeautifulSoup(r2.content, 'html.parser')
    div = s2.find('div', class_='tab-pane fade')
    # Extract the value of the data-product attribute
    try:
      data_product = div['data-product']
    except:
      data_product = s2.find('div',class_='col-form_id-form_2557388242095048 col-md-12 col-lg-12 col-xl-12 col-sm-12 col-xs-12 col-sp-12').find('div')['data-product']
    # Convert the JSON string to a Python dictionary
    product_details = json.loads(data_product)
    manufacturer_id = product_details['id_manufacturer']
    default_shop_id = product_details['id_shop_default']
    reference = product_details['reference']
    supplier_id = product_details['id_supplier']
    price = product_details['price'].split(',')[0].replace('\n', ' ').replace('\r', ' ').strip()
    title = product_details['name']
    description_html = product_details['description']
    description_soup = BeautifulSoup(description_html, 'html.parser')
    description = description_soup.get_text()
    description = html.unescape(description)

    short_description_html = product_details['description_short']
    short_description_soup = BeautifulSoup(short_description_html, 'html.parser')
    short_description = short_description_soup.get_text()
    short_description = html.unescape(short_description)

    category = product_details['category']
    price_tax = product_details['price_tax_exc']
    price_without_reduction = product_details['price_without_reduction']


    products_list.append({
          'manufacturer_id': manufacturer_id,
          'default_shop_id': default_shop_id,
          'reference': reference,
          'supplier_id': supplier_id,
          'price': price,
          'title': title,
          'description': description,
          'short_description': short_description,
          'category': category,
          'price_tax': price_tax,
          'price_without_reduction': price_without_reduction
      })
  try:
    next_page = s_k.find('ul',class_='page-list clearfix text-md-right text-xs-center').find_all('li')[-1]
  except Exception as e:
    print(e)
    next_page = None
  next_page_url = None
  if next_page:
      next_page_url = next_page.find('a').get('href')

  return products_list, next_page_url

def scrape_all_pages(start_url):
    all_data = []
    current_url = start_url

    while current_url:
        print(f"Scraping: {current_url}")
        sys.stdout.flush()
        data, next_page_url = scrape_page(current_url)
        all_data.append(data)
        # if next_page_url == None:
        #   break
        if current_url == next_page_url:
          break
        if next_page_url:
            current_url = next_page_url
        else:
            current_url = None


    return all_data
all_data = []
for url in categories_urls:
  print(f'Scraping for {url} category')
  sys.stdout.flush()
  scraped_data = scrape_all_pages(url)
  all_data.append(scraped_data)

flattened_data = [item for sublist1 in all_data for sublist2 in sublist1 for item in sublist2]

# Create a DataFrame
df = pd.DataFrame(flattened_data)
gs = gc.open_by_key('1Fl00gau4qbcNZMZUQXCkpfXneJSe3ox1wtqL-Shq3Dc')
# select a work sheet from its name
worksheet1 = gs.worksheet('www.kalo.yt')
worksheet1.clear()
set_with_dataframe(worksheet=worksheet1, dataframe=df, include_index=False,
include_column_header=True, resize=True)
print('Google Sheet updated with Df for www.kalo.yt')
sys.stdout.flush()

#------------------------------------------------------------------------------------------------------------

