import streamlit as st
import datetime
import numpy as np
import plotly.graph_objects as go
from stock import Stock
import numpy as np
import pandas as pd
import yfinance as yf
import altair as alt
import streamlit as st
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import schedule
import time
from datetime import datetime, timedelta
import math

# Alpaca
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetAssetsRequest
from alpaca.trading.enums import AssetClass
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.requests import LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame

st.set_page_config(layout="wide", initial_sidebar_state="expanded")
st.title('Algorithmic Trading with QuantumTrading')

# Alpaca Client
trading_client = TradingClient('PKKHMV9Y8C4RN58VNDGX', '1Ra5eWNc99Figh4FHbpFCbq4u0VOz8H4OWfElid9', paper=True)

# Get our account information.
account = trading_client.get_account()
st.markdown('${} is available as buying power.'.format(account.buying_power))

# Check our current balance vs. our balance at the last market close
balance_change = float(account.equity) - float(account.last_equity)
st.markdown(f'Today\'s PnL: ${balance_change}')

# Get a list of all of our positions.
portfolio = trading_client.get_all_positions()

st.markdown("Your asset")
# Print the quantity of shares for each position.
for position in portfolio:
    st.markdown("{} shares of {}".format(position.qty, position.symbol))

# Real time data

# Function to fetch new data and update the chart
def update_chart():
    # Calculate new start and end times
    now = datetime.utcnow()
    start_time = now - timedelta(days=30)  # Fetch a larger time window for historical data
    end_time = now
    
    # Fetching new data
    request_params = CryptoBarsRequest(
        symbol_or_symbols=["BTC/USD"],
        timeframe=TimeFrame.Minute,
        start=start_time,
        end=end_time
    )
    btc_bars = client.get_crypto_bars(request_params).df  # Assuming .df is used to access the DataFrame
    
    # Append new data to the existing chart
    fig.add_trace(go.Candlestick(x=btc_bars.index, open=btc_bars.open, high=btc_bars.high, low=btc_bars.low, close=btc_bars.close))

# Real-time data setup
client = CryptoHistoricalDataClient()

# Calculate the start and end times for the initial data (one month from today)
initial_start_time = datetime.utcnow() - timedelta(days=30)
initial_end_time = datetime.utcnow()

# Initial data request
initial_request_params = CryptoBarsRequest(
    symbol_or_symbols=["BTC/USD"],
    timeframe=TimeFrame.Minute,
    start=initial_start_time,
    end=initial_end_time
)
btc_bars = client.get_crypto_bars(initial_request_params) 
df = btc_bars.df
df = df.reset_index()
df = df.drop(columns=['symbol']).set_index('timestamp')

# Streamlit setup
st.subheader('CANDLESTICK CHART')
fig = go.Figure()
fig = make_subplots(rows=1, cols=1)
fig.add_trace(go.Candlestick(x=df.index, open=df.open, high=df.high, low=df.low, close=df.close))
fig.update_layout(xaxis_title="Date", yaxis_title="Price", width=760, height=600, template="plotly_dark")
st.plotly_chart(fig)

###############################################################################################################

st.subheader('TRADING BOT')
from datetime import datetime, timedelta
import math
import time

SYMBOL = 'BTCUSD'
SMA_FAST = 12
SMA_SLOW = 24
QTY_PER_TRADE = 1


# Description is given in the article
def get_pause():
    now = datetime.now()
    next_min = now.replace(second=0, microsecond=0) + timedelta(minutes=1)
    pause = math.ceil((next_min - now).seconds)
    print(f"Sleep for {pause}")
    return pause

# Same as the function in the random version
def get_position(symbol):
    # Assuming trading_client.get_open_position(symbol) returns the position information
    position = trading_client.get_open_position(symbol)

    # Check if the position is available
    if position:
        # Extract and return the quantity (qty)
        return float(position.qty)
    else:
        # If position is not available, return 0
        return 0

# Returns a series with the moving average
def get_sma(series, periods):
    return series.rolling(periods).mean()

# Checks whether we should buy (fast ma > slow ma)
def get_signal(fast, slow):
    print(f"Fast {fast[-1]}  /  Slow: {slow[-1]}")
    return fast[-1] > slow[-1]

# Get up-to-date 1 minute data from Alpaca and add the moving averages
def get_bars(symbol):

    # Calculate the nearest past minute
    current_time = datetime.utcnow()
    nearest_minute = current_time - timedelta(minutes=current_time.minute % 1, seconds=current_time.second, microseconds=current_time.microsecond)

    # Set the end time to the nearest past minute
    end_time = nearest_minute - timedelta(minutes=1)

    # Set the start time (e.g., 1 minute before the end time)
    start_time = end_time - timedelta(minutes=1)

    # Request 1-minute data
    request_params = CryptoBarsRequest(
        symbol_or_symbols=[symbol],
        timeframe=TimeFrame.Minute,
        start=start_time,
        end=end_time
    )

    btc_bars = client.get_crypto_bars(request_params) 
    bars = btc_bars.df
    bars = df.reset_index()
    bars = df.drop(columns=[symbol]).set_index('timestamp')
    bars[f'sma_fast'] = get_sma(bars.close, SMA_FAST)
    bars[f'sma_slow'] = get_sma(bars.close, SMA_SLOW)
    return bars


while True:

    SYMBOL = "BTC/USD"
    SMA_FAST = 12
    SMA_SLOW = 24
    QTY_PER_TRADE = 1
    
    # GET DATA
    bars = get_bars(SYMBOL)
    # CHECK POSITIONS
    position = get_position(SYMBOL)
    should_buy = get_signal(bars.sma_fast,bars.sma_slow)
    print(f"Position: {position} / Should Buy: {should_buy}")
    if position == 0 and should_buy == True:
        # WE BUY ONE BITCOIN
        # api.submit_order(SYMBOL, qty=QTY_PER_TRADE, side='buy')
        print(f'Symbol: {SYMBOL} / Side: BUY / Quantity: {QTY_PER_TRADE}')
    elif position > 0 and should_buy == False:
        # WE SELL ONE BITCOIN
        # api.submit_order(SYMBOL, qty=QTY_PER_TRADE, side='sell')
        print(f'Symbol: {SYMBOL} / Side: SELL / Quantity: {QTY_PER_TRADE}')

    time.sleep(get_pause())
    print("*"*20)
