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

start_time = datetime.now()
f_start_time = start_time.strftime('%Y-%m-%d %H:%M:%S')


headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'}


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

json_credentials = {
  "type": "service_account",
  "project_id": "calender-407115",
  "private_key_id": "d19bdf8bbf41a641ffc0541d4c971d8af5cd5c13",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCuZDUV7SBF5TnA\nLjV4yuSB6g6upb/nkYcfVCBDPccKca2G7F4HMFiz55s3aHS5lSgKxEu6/EmIWUWP\nF1BRWhVTjtXxdMJup+2lTIf4t/bgOkqyvf+/GyX1r99Tuxr+Eg7Leq684nzhvWV6\nNyBLjU7bgdo55OsdOFwZ1Tfb6P+CPy3lYzTwchys0Ejk74/eRpxyRgi+HfgYs0VS\nLqw6olrtrAa+xYDJcvixP4WYl06vhOJ5L0KZnev/4ympxQSuqVGuXf1bobB4/PSM\nXcGC9fkSJePH3xew5FKHnFvvb6bQ5qn0cMv1MVOK0L+ABQvmyXo0U6gzRwKCL3z6\n3/kKPt+FAgMBAAECggEAGnQY7rqJqrtFh2F7EFe2p1OvO87ozWJwnM/7ajfKJEtv\nhzKpEMNvW9rw20wnvf8M6T/dklUIJ9Fi5nx4MomiXTUi6ahMgNH4ZUVhWtk3xHZo\niQnz7DQHY2gfoxPphEuOSE9+h33TyRUcekLieJN24tVPxSMfMc+FfmWu6NeZ6qfA\nCDH0ALHM3bGCrpWEuHN6iu2vQbwXv5tKFhoPeTe4hkpN6Wuk59qWgumVdo12D8K7\nzkLJryklapauEWurT1Cbi4yCTGXc0xAhg4vxC9kBmIsjKdMtjnPUKkFeUDc3WfKP\ntH4zcLNlBuglO7/3gDxIIwn2AdCeb6o0+6ZgtrqyAQKBgQDWBwXiTNvMRCvPdj3h\nAW9+uyowEJXIdrPflK6ZOHsuqz+7NiWTKoYFbv57+4oHsRYAOkql6soVorfMde12\nhO8YpS3guUROz2Fm/vgESKo7isIGt6L36hndrpHT2r3OhtxhNI4PDQHmKmVQl+fP\n8XuZOTt2K43Xb6BSrDvBeUMtTwKBgQDQl08jMFj8gfRlYOLnFiyZ6Sm64+aRh2m5\nEbg9XJyNi/bDD2IICYOEFBsNuuqeI2zwF2AmYkG6Y1AV2i78tne+5zHz4818w15R\ntxOhJbX4IfsMCv1x3QEMy01VFlZ09o60hDJ3B5jku9Ksm+T6lGH9Skj+FmKjX8u/\n2x8XgOU46wKBgGIwIqDpRcT2WWr6AfVh5TaswvP+B9lJq8ecvGUKpmiIo9pNQvu6\n/HUtsI5Mncxdj4xXMbvgdQlr9wpT57cB0XbrAJsiI5ZMSZEo07uTYpWiWNUgFiHK\nQkeTOM+KgJ1o/V2S8MEy5HYlaQmKRwz86gknWoIiBRaa3WBQJ7Hg4dK9AoGASg6u\nhivQLDZncubnKGxzAWIK8tOfNOQC4TYtV3veCVM8FR0NDRVzoB0TTdijG+ov7z4d\nYQNZmrdP47JHJGoUMa8byR+EAVvLzO9XBMvCw4os+6WbPiXdDZHQrvjzUSuIlwao\ndCI6Yltc/POMZHryH1+UcsG325FTYZaGf22/9GkCgYEAy1Gyl1IGdxtBWVIO40gV\nNwQ2Dpj11+cBssFsts8GoTPcpEY2+wVYZ2X7OPlgu+lqACY+ahzn/TTrU8cQ7qKL\nnn4d5ejTPVWpt65EprvUtM9ktfNGlbhMWfD2NFfJuADvO0viHUhPHRhwYoEAEWlK\n+DiZMK30YbupxN5rje8hdbU=\n-----END PRIVATE KEY-----\n",
  "client_email": "calender-try@calender-407115.iam.gserviceaccount.com",
  "client_id": "112124438999230222753",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/calender-try%40calender-407115.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}


SERVICE_ACCOUNT_FILE = json_credentials
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SAMPLE_SPREADSHEET_ID = "1E_vWDp1LOxkdm17nNR16Em3rjXwYA_5H8ssbANWXmIU"

SAMPLE_RANGE_NAME = "www.ballou976.com"
creds = None
creds = service_account.Credentials.from_service_account_info(json_credentials, scopes=SCOPES)

service = build("sheets", "v4", credentials=creds)


def update_google_sheet(sheet_id, range_name, df):
    # Authenticate with Google Sheets API using service account credentials
    credentials = service_account.Credentials.from_service_account_info(json_credentials)
    service = build('sheets', 'v4', credentials=credentials)

    # Convert DataFrame to list of lists
    data = [df.columns.tolist()] + df.values.tolist()

    # Update values in Google Sheet
    request = service.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range=range_name,
        valueInputOption='RAW',
        body={'values': data}
    )
    response = request.execute()
    print('Data updated successfully for www.ballou976.com')
    sys.stdout.flush()

update_google_sheet(SAMPLE_SPREADSHEET_ID, SAMPLE_RANGE_NAME , df)


#------------------------------------------------------------------------------------------------------------

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

# start_url = "https://kalo.yt/fr/10-gros-electromenager"  # Starting URL
# all_scraped_data = scrape_all_pages(start_url)
all_data = []
for url in categories_urls:
  print(f'Scraping for {url} category')
  sys.stdout.flush()
  scraped_data = scrape_all_pages(url)
  all_data.append(scraped_data)

flattened_data = [item for sublist1 in all_data for sublist2 in sublist1 for item in sublist2]

# Create a DataFrame
df = pd.DataFrame(flattened_data)

json_credentials = {
  "type": "service_account",
  "project_id": "calender-407115",
  "private_key_id": "d19bdf8bbf41a641ffc0541d4c971d8af5cd5c13",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCuZDUV7SBF5TnA\nLjV4yuSB6g6upb/nkYcfVCBDPccKca2G7F4HMFiz55s3aHS5lSgKxEu6/EmIWUWP\nF1BRWhVTjtXxdMJup+2lTIf4t/bgOkqyvf+/GyX1r99Tuxr+Eg7Leq684nzhvWV6\nNyBLjU7bgdo55OsdOFwZ1Tfb6P+CPy3lYzTwchys0Ejk74/eRpxyRgi+HfgYs0VS\nLqw6olrtrAa+xYDJcvixP4WYl06vhOJ5L0KZnev/4ympxQSuqVGuXf1bobB4/PSM\nXcGC9fkSJePH3xew5FKHnFvvb6bQ5qn0cMv1MVOK0L+ABQvmyXo0U6gzRwKCL3z6\n3/kKPt+FAgMBAAECggEAGnQY7rqJqrtFh2F7EFe2p1OvO87ozWJwnM/7ajfKJEtv\nhzKpEMNvW9rw20wnvf8M6T/dklUIJ9Fi5nx4MomiXTUi6ahMgNH4ZUVhWtk3xHZo\niQnz7DQHY2gfoxPphEuOSE9+h33TyRUcekLieJN24tVPxSMfMc+FfmWu6NeZ6qfA\nCDH0ALHM3bGCrpWEuHN6iu2vQbwXv5tKFhoPeTe4hkpN6Wuk59qWgumVdo12D8K7\nzkLJryklapauEWurT1Cbi4yCTGXc0xAhg4vxC9kBmIsjKdMtjnPUKkFeUDc3WfKP\ntH4zcLNlBuglO7/3gDxIIwn2AdCeb6o0+6ZgtrqyAQKBgQDWBwXiTNvMRCvPdj3h\nAW9+uyowEJXIdrPflK6ZOHsuqz+7NiWTKoYFbv57+4oHsRYAOkql6soVorfMde12\nhO8YpS3guUROz2Fm/vgESKo7isIGt6L36hndrpHT2r3OhtxhNI4PDQHmKmVQl+fP\n8XuZOTt2K43Xb6BSrDvBeUMtTwKBgQDQl08jMFj8gfRlYOLnFiyZ6Sm64+aRh2m5\nEbg9XJyNi/bDD2IICYOEFBsNuuqeI2zwF2AmYkG6Y1AV2i78tne+5zHz4818w15R\ntxOhJbX4IfsMCv1x3QEMy01VFlZ09o60hDJ3B5jku9Ksm+T6lGH9Skj+FmKjX8u/\n2x8XgOU46wKBgGIwIqDpRcT2WWr6AfVh5TaswvP+B9lJq8ecvGUKpmiIo9pNQvu6\n/HUtsI5Mncxdj4xXMbvgdQlr9wpT57cB0XbrAJsiI5ZMSZEo07uTYpWiWNUgFiHK\nQkeTOM+KgJ1o/V2S8MEy5HYlaQmKRwz86gknWoIiBRaa3WBQJ7Hg4dK9AoGASg6u\nhivQLDZncubnKGxzAWIK8tOfNOQC4TYtV3veCVM8FR0NDRVzoB0TTdijG+ov7z4d\nYQNZmrdP47JHJGoUMa8byR+EAVvLzO9XBMvCw4os+6WbPiXdDZHQrvjzUSuIlwao\ndCI6Yltc/POMZHryH1+UcsG325FTYZaGf22/9GkCgYEAy1Gyl1IGdxtBWVIO40gV\nNwQ2Dpj11+cBssFsts8GoTPcpEY2+wVYZ2X7OPlgu+lqACY+ahzn/TTrU8cQ7qKL\nnn4d5ejTPVWpt65EprvUtM9ktfNGlbhMWfD2NFfJuADvO0viHUhPHRhwYoEAEWlK\n+DiZMK30YbupxN5rje8hdbU=\n-----END PRIVATE KEY-----\n",
  "client_email": "calender-try@calender-407115.iam.gserviceaccount.com",
  "client_id": "112124438999230222753",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/calender-try%40calender-407115.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}


SERVICE_ACCOUNT_FILE = json_credentials
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SAMPLE_SPREADSHEET_ID = "1E_vWDp1LOxkdm17nNR16Em3rjXwYA_5H8ssbANWXmIU"

SAMPLE_RANGE_NAME = "www.kalo.yt"
creds = None
creds = service_account.Credentials.from_service_account_info(json_credentials, scopes=SCOPES)

service = build("sheets", "v4", credentials=creds)


def update_google_sheet(sheet_id, range_name, df):
    # Authenticate with Google Sheets API using service account credentials
    credentials = service_account.Credentials.from_service_account_info(json_credentials)
    service = build('sheets', 'v4', credentials=credentials)

    # Convert DataFrame to list of lists
    data = [df.columns.tolist()] + df.values.tolist()

    # Update values in Google Sheet
    request = service.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range=range_name,
        valueInputOption='RAW',
        body={'values': data}
    )
    response = request.execute()
    print('Data updated successfully for www.kalo.yt')
    sys.stdout.flush()

update_google_sheet(SAMPLE_SPREADSHEET_ID, SAMPLE_RANGE_NAME , df)

