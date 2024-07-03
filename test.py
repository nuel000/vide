import os
import re
from google.oauth2 import service_account
from googleapiclient.discovery import build
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
import sys

start_time = datetime.now()
f_start_time = start_time.strftime('%Y-%m-%d %H:%M:%S')


headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'}

scopes = ['https://www.googleapis.com/auth/spreadsheets',
          'https://www.googleapis.com/auth/drive']
json_credentials = json.loads(os.environ['GOOGLE_APPLICATION_CREDENTIALS'])
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SAMPLE_SPREADSHEET_ID = "10ublPdt4Q3Q2glrqR__VZF2Cf4lq5h6B73WPX3AjkGI"
SAMPLE_RANGE_NAME = "Sheet1"

creds = service_account.Credentials.from_service_account_info(json_credentials, scopes=SCOPES)
gc = gspread.authorize(creds)
gauth = GoogleAuth()
drive = GoogleDrive(gauth)
print('Authorized')
sys.stdout.flush()


data = {
    'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
    'Age': [24, 27, 22, 32, 29],
    'City': ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix']
}
df = pd.DataFrame(data)
gs = gc.open_by_key('10ublPdt4Q3Q2glrqR__VZF2Cf4lq5h6B73WPX3AjkGI')
# select a work sheet from its name
worksheet1 = gs.worksheet('Sheet1')
worksheet1.clear()
set_with_dataframe(worksheet=worksheet1, dataframe=df, include_index=False,
include_column_header=True, resize=True)
print('Google Sheet updated with Df for www.ballou976.com')
sys.stdout.flush()
