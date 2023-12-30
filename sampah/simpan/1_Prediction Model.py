import streamlit as st
import datetime
import numpy as np
import plotly.graph_objects as go
from stock import Stock
import numpy as np
import pandas as pd
import yfinance as yf

st.set_page_config(layout="wide", initial_sidebar_state="expanded")
# st.title('Model I QuantumTrading')

#used in all tabs
STOCKS = np.array([ "BTC-USD", "ETH-USD", "BNB-USD",'XRP-USD']) 
tickers = STOCKS
dropdown = st.multiselect("Choose your currency", tickers)

tab1, tab2 = st.tabs(["Historical Data","Prediction"])

with tab1:

    col1, col2 = st.columns(2)

    with col1:
        start = st.date_input('Start', value = pd.to_datetime('2023-01-01'))
    with col2:
        end = st.date_input('End', value = pd.to_datetime('today'))

    def relativeret(df):
        rel = df.pct_change()
        cumret = (1+rel).cumprod()-1
        cumret = cumret.fillna(0)
        return cumret
    
    if len(dropdown)>0:
        df=relativeret(yf.download(dropdown,start,end)['Adj Close'])
        st.line_chart(df)

with tab2:

    HORIZON = st.number_input(
        "Prediction Period", min_value=7, max_value=200, key="HORIZON"
        )


    def relativeret(df):
        rel = df.pct_change()
        cumret = (1+rel).cumprod()-1
        cumret = cumret.fillna(0)
        return cumret
    
    if len(dropdown)>0:
        df=relativeret(yf.download(dropdown,start,end)['Adj Close'])
        st.line_chart(df)
  


