import configparser as cfg
import json
import logging
import time
import datetime

import requests
from requests import HTTPError
from telegram import *;
from telegram.ext import *;


logging.basicConfig( format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    # take time,level,name
                    level=logging.INFO)
logger = logging.getLogger(__name__)

def fetchData(pincode, date):
    date = '02-05-2021'
    url = 'https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByPin?pincode=' + pincode + '&date=' + date
    headers = {
        'accept': 'application/json', 'Accept-Language': 'hi_IN',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    try:
        response = requests.get(url, headers=headers)
        if (response.status_code == 200):
            jsonResponse = response.json()
            logger.info("Fetching data for pincode: %s", pincode)
            logger.info("Response: %s", jsonResponse)
            if (len(jsonResponse['sessions']) != 0):
                return json.dump(jsonResponse)
            else:
                return "No Slots"
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')

from datetime import date

# today = date.today()
# d1= date.today().strftime("%d-%m-%y")
# print("Today's date:", d1)

date = datetime.datetime.now()
for i in range(15):
    date += datetime.timedelta(days=i)
    print(date.strftime("%d-%m-%y"))