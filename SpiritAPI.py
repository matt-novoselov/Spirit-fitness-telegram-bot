import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

load_dotenv()

cookies = {
    'BITRIX_SM_UIDH': os.getenv("BITRIX_SM_UIDH"),
    'BITRIX_SM_UIDL': os.getenv("BITRIX_SM_UIDL"),
}

def GetMonthVisit():
    response = requests.get('https://spiritfit.ru/personal/', cookies=cookies)
    soup = BeautifulSoup(response.content, 'html.parser')
    monthly_visit = soup.find("input", {"id": "form_poseshcheniya_test_1430"})['value']
    return int(monthly_visit)