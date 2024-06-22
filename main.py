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
  "project_id": "bright-coyote-426808-p6",
  "private_key_id": "d9907f37cf916424119a237535a94ba1d05ff220",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQDUVmWvcsc4kX4I\nFIw55J6pm631NZWI1nvbrVZhVSfatxkno7VAGNStf2atwtbXhFVDHFR1TxBpBMbR\nBzVQ2KKYKYb3gimwHKRL51J2nhQUj7zr26qEuYVRAaSFoSbVjaGgtxDNX5dKQ/vO\npZojoeNSaXCi6Mox92qy7+ztrYg2/B81ahvQ3481qR2paOSpubFjT/2ndegWIRs0\npsB0j1lZ5CWrgH5Uu8ouJuaMhU+bTZXFa9rqhDbR+ebBJ1rYknffNaAadhbacNTh\njHY6MJvysO3l4YghyNSpt6fetgtLt0KKEsYK5sOC1kA0UJPbxRy6yDFFkFhKBMvZ\nA8MXIWaZAgMBAAECggEAB8VATrhg6Vq3Ba1YKFzhIDct7uBOyvAryNvst6kkc+Y+\nycA9nM02fexAogaUUtS+mLMhCsihmBua+av4MS+MW7cr/5jIKnAR5Hk1qljvRoVa\nwOLhYvQLGJjPytgdPLQZ1cYn8OwY9EMipEBT22P27AgnHWnEJH9NF06dGWGVWjW0\nqr2C+lteys3XS7JD/AdkLjczYbj2eRM7+9G56b89t+Y1IHEYt9fVUMS61MA8TPs4\nXUWJ1+55IYKK7iJ5rxE5YQonAD7u7TjhVPMsShbrSu1RaTKNGfcfoiiR2HBVuUVr\nCCjK8qHZ8QOrVy/yZeKl2jjDGbxjMZP4vzZNA8RhRQKBgQD9lUCvGecbI1fdTdik\naBIomGmt+8IbyHMEDdKtNMn8kGDiJON/QcpkWeOCi9cevj4ochpcxmWU27G6RmVa\ntjoZt9aVzLig6GKrSrohqEXyqC7PrLIs3a9qaR8D8pZs+sBTwxFSqSQU26no5I7Z\nRUuiQWgxqWjDjtnd5qBmR5rf6wKBgQDWXIEyF60UF8zh1a+qt33iEeCN+t4CzvBV\nqRVJbEPxZBTR4mLyqbV2s30uHk/Keder5OxTZQUUUZ2gSsm0ihJMVeObpGKSAHNL\nKNMfhwG/Zx7rd2s95IrRDJeAV1fafSz7fTIBnzqiG4bRwjASavR4x7px1zOLIM2I\nPSMdrxr2iwKBgQD6Af2M5QfR3K2S1V4i8Sv99A4050J/q8ehlpNACwydQicSrnXQ\nkCefenPw0Dgd6khUDfLpxvx9n4AA+8iPf5uWoYYhmH3qvlIRORJ7fnDABYppW4Uq\n8MEyM0PN24ztEuctbeOVUIbvPYatwzEHCue/p6a3V6OfMiagPPGlBTGvUwKBgQCt\nnc6mG7b7ByvR3Zih1GwIpiIR3JXkAGd3ebLb/OwqnryeIZWypPFsaoOAztwhSf38\nIzWldbRfeJsKMIidyRZ47Tej38hWKDc5MJ+OcXJg68yHOfmJ74jfOCucryFgvPGp\n3wSZe7WphlHzoiv9PtMy39GKUppUnQTay2mdqS1VcQKBgQDsnbCl9KkcEzC7+k9G\ny69Y+d+tnXUlSHDU+WYEdsFx0AcrHcorwhYHRR4E4wHdHQwChfWaaOjnSP5Z/PDh\n8k9MWd4a9MAEb2y/4HqtcnKpu/SRh/oJ5tNd92KEZaZn35FlX9AKgUnmJHwe7Yn7\nhTOsqopNeLNmxL9yABh1Xb8D6g==\n-----END PRIVATE KEY-----\n",
  "client_email": "python-api@bright-coyote-426808-p6.iam.gserviceaccount.com",
  "client_id": "109775724169581285261",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/python-api%40bright-coyote-426808-p6.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

SERVICE_ACCOUNT_FILE = json_credentials
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SAMPLE_SPREADSHEET_ID = "1Fl00gau4qbcNZMZUQXCkpfXneJSe3ox1wtqL-Shq3Dc"

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
    print('Data updated successfully.')
update_google_sheet(SAMPLE_SPREADSHEET_ID, SAMPLE_RANGE_NAME ,df)
print('Google Sheet updated with Df for www.ballou976.com')
sys.stdout.flush()
