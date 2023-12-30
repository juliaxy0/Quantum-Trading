import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt
import yfinance as yf
import streamlit as st 
import plotly.graph_objects as go
import plotly.express as px
from wallet.luno import Luno
from streamlit_extras.chart_annotations import get_annotations_chart 
import requests
from requests.exceptions import ConnectionError
from bs4 import BeautifulSoup
import time

st.set_page_config(layout="wide")

st.title('CRYPTO WALLET ANALYSIS')

######################################################################### INITIALIZING ALL CRYPTO DATA #####################################################################################

# Initializing luno wallet
username = '5te86qwu2bmk'
password ='9ZuWZ6K6t6hak8lkwAvSIxhKjvUhdgVmuqs-dp677As'
luno = Luno(username,password)

# Fetch wallet data
@st.cache_data(show_spinner=False)
def get_luno_data():
    luno_wallet = luno.get_assets()
    return luno_wallet

luno_wallet = get_luno_data()

#Initialize luno data
luno_data = []

# Loop through assets and append to the array
for asset,balance in luno_wallet:
    if asset == "MYR":
        continue  # Skip displaying the button for MYR
    luno_data.append((asset, balance))

# Modify the asset name directly in the luno_wallet data
luno_data = [(asset.replace('XBT', 'BTC'), balance) for asset, balance in luno_data]

# Initialize binance dummy data
binance_data = [
    ('BTC', '31.00'),
    ('DOT', '20.0021'),
    ('DOGE', '23.0916'),
    ('ETH', '15.0026'),
    ('XRP', '11.9255'),
    ('LINK', '30.9255')
]
# Create a dictionary to store the total balances
total_balances = {}

# Calculate the total balance for Luno data
for asset, balance in luno_data:
    total_balances[asset] = total_balances.get(asset, 0) + float(balance)

# Calculate the total balance for Binance data
for asset, balance in binance_data:
    total_balances[asset] = total_balances.get(asset, 0) + float(balance)

##################################################################################### DATAFRAME  #######################################################################################

df_total_crypto = pd.DataFrame(list(total_balances.items()), columns=['Asset', 'Balance'])
crypto_assets = [asset + '-USD' for asset in df_total_crypto['Asset'].tolist()]
df_luno = pd.DataFrame(list(luno_data), columns=['Asset', 'Balance'])
df_binance = pd.DataFrame(list(binance_data), columns=['Asset', 'Balance'])

################################################################################## SIDEBAR WALLET DASHBOARD  ###################################################################################

#  Dashboard container
sidebar_wallet = st.sidebar.container()

with sidebar_wallet.expander("Luno Wallet"):
    # Display data in one column
    for currency, amount in luno_data:
        st.write(f"{currency}: {amount}")

with sidebar_wallet.expander("Binance Wallet"):
    # Display data in one column
    for currency, amount in binance_data:
        st.write(f"{currency}: {amount}")

sidebar_wallet.button("Add Wallet", type="primary")

######################################################################### FETCHING ALL CRYPTO DATA #####################################################################################

def web_content_div(web_content, class_path):
    web_content_div = web_content.find_all('div', {'class': class_path})
    try:
        spans = web_content_div[0].find_all('fin-streamer')
        texts = [span.get_text() for span in spans]
    except IndexError:
        texts = []
    return texts

@st.cache_data(show_spinner=False)
def real_time_price(crypto_code):
    url = 'https://finance.yahoo.com/quote/' + crypto_code + '?p=' + crypto_code + '&.tsrc=fin-srch'
    try:
        r = requests.get(url)
        web_content = BeautifulSoup(r.text, 'lxml')
        texts = web_content_div(web_content, 'D(ib) Mend(20px)')
        if texts:
            price, change, percent = texts[0], texts[1], texts[2]
        else:
            price, change, percent = [], [], []
    except ConnectionError:
        price, change, percent = [], [], []
    return price, change, percent

@st.cache_data(show_spinner=False)
def get_table_data(crypto_assets):
    table_data = []

    for crypto_asset in crypto_assets:
        # Get real-time price information
        price, change, percent = real_time_price(crypto_asset)

        # Append the dictionary with additional columns
        table_data.append({
            'Asset': crypto_asset,
            'Price': price,
            'Change': change + " " + percent
        })

    return table_data

##################################################################################  WALLET  DASHBOARD  ########################################################################################

#  Dashboard container
dashboard = st.container()

# Display in markdown
dashboard.markdown("## Total Crypto")
# for asset, total_balance in total_balances.items():
#     formatted_total_balance = '{:.4f}'.format(total_balance)
#     button_key = f"{asset}_button"  # Ensure a unique key for each button
#     button_clicked = dashboard.button(label=f"**{asset}**, {formatted_total_balance}", key=button_key)

fig1 = px.pie(df_total_crypto, values='Balance', names='Asset', color_discrete_sequence=px.colors.sequential.RdBu)
fig1.update_layout(width=600, height=400)
dashboard.plotly_chart(fig1)

# Create an initial empty slot for the table
table_slot = st.empty()
table_data = get_table_data(crypto_assets)
table_slot.table(pd.DataFrame(table_data))
