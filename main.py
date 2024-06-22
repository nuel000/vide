import re
import json
import requests
import subprocess
import pandas as pd
from bs4 import BeautifulSoup
import pandas as pd
import gspread
from gspread_dataframe import set_with_dataframe
from google.oauth2.service_account import Credentials
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import html
from datetime import datetime

start_time = datetime.now()
f_start_time = start_time.strftime('%Y-%m-%d %H:%M:%S')


headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'}

scopes = ['https://www.googleapis.com/auth/spreadsheets',
          'https://www.googleapis.com/auth/drive']

credentials = Credentials.from_service_account_file('lambert_credentials.json', scopes=scopes)
gc = gspread.authorize(credentials)

gauth = GoogleAuth()
drive = GoogleDrive(gauth)


import requests
from bs4 import BeautifulSoup

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

# Save the DataFrame to a CSV file
df.to_csv('product_data_df.csv', index=False, encoding='utf-8-sig')
# open a google sheet
gs = gc.open_by_key('1Fl00gau4qbcNZMZUQXCkpfXneJSe3ox1wtqL-Shq3Dc')
# select a work sheet from its name
worksheet1 = gs.worksheet('www.ballou976.com')
worksheet1.clear()
set_with_dataframe(worksheet=worksheet1, dataframe=df, include_index=False,
include_column_header=True, resize=True)
print('Google Sheet updated with Df for www.ballou976.com')
