import pandas as pd
import streamlit as st
import matplotlib.pyplot as pltenv
from robot import robotClass
from alpacas import alpacaClass
import time

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

alpaca_user = alpacaClass()
robot_user = robotClass()

tab1, tab2, tab3 = st.tabs(["Technical Analysis", "Sentiment Analysis", "Prediction"])

with tab1: 
    st.markdown("Technical Analysis")



with tab2:
    csv_file_path = "regressor/assetsummaries.csv"
    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_file_path)

    selected_columns = ['Ticker', 'Summary', 'Sentiment', 'URL']
    df_selected = df[selected_columns]

    # Display the DataFrame with selected columns
    st.table(df_selected)

with tab3: 
    st.markdown("Prediction")


# Loop to fetch current minute's data every 10 seconds
while True:

    # Fetch real-time data
    alpaca_user.fetch_real_time_btc_data()
    alpaca_user.fetch_real_time_eth_data()
    alpaca_user.fetch_real_time_ltc_data()
    alpaca_user.fetch_real_time_link_data()
    alpaca_user.getAccountDetails()
    alpaca_user.get_asset()
    alpaca_user.cleanFiles()
    robot_user.updateProfit()


    # Wait for 10 seconds before the next iteration
    time.sleep(1)
