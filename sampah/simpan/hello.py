import pandas as pd
import datetime
import requests
from requests.exceptions import ConnectionError
from bs4 import BeautifulSoup

def web_content_div(web_content, class_path):
    web_content_div = web_content.find_all('div', {'class': class_path})
    try:
        spans = web_content_div[0].find_all('fin-streamer')
        texts = [span.get_text() for span in spans]
    except IndexError:
        text = []
    return texts

def real_time_price(crypto_code):
    url = 'https://finance.yahoo.com/quote/' + crypto_code + '?p=' + crypto_code
    try:
        r = requests.get(url)
        web_content = BeautifulSoup(r.text, 'lxml')
        texts = web_content_div(web_content, 'D(ib) Mend(20px)')
        if texts != []:
            price, change, status  = texts[0], texts[1], texts[2]
        else:
            price,change,status = [],[],[]
    except ConnectionError:
        price,change = [],[]
    return price, change, status


crypto = ['BTC-USD']
print(real_time_price('BTC-USD'))