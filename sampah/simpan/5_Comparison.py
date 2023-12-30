import streamlit as st
import datetime
import numpy as np
import plotly.graph_objects as go
from stock import Stock
import numpy as np
import pandas as pd
import yfinance as yf
import altair as alt

st.set_page_config(layout="wide", initial_sidebar_state="expanded")
st.title('Algorithmic Trading with QuantumTrading')

#used in all tabs
STOCKS = np.array([ "BTC-USD", "ETH-USD", "BNB-USD",'XRP-USD']) 
tickers = STOCKS
dropdown = st.multiselect("Choose your currency", tickers, default=["BTC-USD"])

tab1, tab2 = st.tabs(["Historical Data","Prediction"])

with tab1:

    col1, col2 = st.columns(2)

    with col1:
        start = st.date_input('Start', value = pd.to_datetime('2023-05-01'))
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

    # Manually add a vertical line using Altair
    line_date = '2022-11-01'  # Replace with the desired date for the vertical line

    # Altair chart
    alt_chart = alt.Chart(df.reset_index()).mark_rule(color='red').encode(
        x='Date:T',
    ).transform_filter(
        alt.datum.Date == line_date
    )

  


