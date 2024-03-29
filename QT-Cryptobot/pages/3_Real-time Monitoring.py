import streamlit as st
import time
from alpacas import alpacaClass
from robot import robotClass
from stratergies import stratergiesClass
from PIL import Image
import pandas as pd
from streamlit_extras.app_logo import add_logo
from datetime import datetime

st.set_page_config(layout="wide", initial_sidebar_state="collapsed", page_title="Real-time Monitoring", page_icon = ":money_with_wings:")

# Get parameter from link for auth
username_param = st.experimental_get_query_params().get("id", [""])[0]

add_logo("pics/logo.png")

with st.sidebar:

    sidebarContainer = st.empty()


    if st.button("Logout"):
        st.markdown(f'<meta http-equiv="refresh" content="0;URL=http://localhost:8501/">', unsafe_allow_html=True)
        
css = '''
<style>
    [data-testid='stSidebarNav'] > ul {
        min-height: 43vh;
    }
</style>
'''
st.markdown(css, unsafe_allow_html=True)

############################################# Real time Dashboard #####################################

# Dashboard title
st.subheader("Real-time Crypto Analysis and Monitoring")
st.caption("Stay updated with live analysis and monitoring of cryptocurrency trends as they happen.")
st.markdown("")

# Create alpaca user
alpaca_user = alpacaClass(username_param)
robot_user = robotClass(username_param)

# Images of each crypto
pic2 = Image.open("pics/2.png")
pic4 = Image.open("pics/4.png")
pic6 = Image.open("pics/6.png")
pic8 = Image.open("pics/8.png")
scale = Image.open("pics/scale.png")
up_image = Image.open("pics/up.png")
down_image = Image.open("pics/down.png")
arrow = Image.open("pics/arrow.png")
more_image = Image.open("pics/more.png")

# How we scale our sentiment and ML analysis explanation to user
eduContainer = st.container(border=True)

with eduContainer:

    c, sentimenEdu, MLEdu, d  = st.columns([0.05,0.8, 0.8, 0.05])

    with c:
        st.markdown("")

    with sentimenEdu:
        st.image(scale, width=600, use_column_width=False)

    with MLEdu:
        st.image(arrow, width=600, use_column_width=False)
        
statusContainer = st.container()

with statusContainer:

    btc, eth, link, ltc = st.columns([1,1,1,1])

    with btc:
        btcContainer = st.container(border=True)
        with btcContainer:
            btcPlaceholder = st.empty() 

    with eth:
        ethContainer = st.container(border=True)
        with ethContainer:
            ethPlaceholder = st.empty() 
     
    with link:
        linkContainer = st.container(border=True)
        with linkContainer:
            linkPlaceholder = st.empty() 
         
    with ltc:
        ltcContainer = st.container(border=True)
        with ltcContainer:
            ltcPlaceholder = st.empty() 

            

# creating a single-element container
placeholder = st.empty()

with placeholder.container():

    live, buy = st.columns([1, 0.33])

    with live:


        tradingview_widget_code = """
        <iframe src="https://s.tradingview.com/embed-widget/advanced-chart/?symbol=BTCUSD&amp;interval=1&amp;timezone=Asia%2FSingapore&amp;theme=dark&amp;style=1&amp;locale=en&amp;enable_publishing=false&amp;hide_side_toolbar=false&amp;allow_symbol_change=true&amp;studies=%5B%5D&amp;show_popup_button=true&amp;popup_width=1000&amp;popup_height=70" style="width: 100%; height: 498px;" frameborder="0" allowtransparency="true" allowfullscreen="true" scrolling="no"></iframe>
        """

        # Display the TradingView widget using an iframe
        st.markdown(tradingview_widget_code, unsafe_allow_html=True)

    with buy:

        # Fetch real-time data
        real_time_prices =  alpaca_user.getRealTimePrices()
        latest_cash = alpaca_user.get_latest_cash()

        # Manual order form
        with st.form("my_form"):
            st.subheader("Create an order", help="Manual orders are not currently being recorded or tracked for profit.")
            st.text_input("Available Cash:", value=f"${latest_cash}", key="cash", disabled=True)
            symbol = st.selectbox("Select Crypto Symbol:", options=['BTC/USD', 'ETH/USD', 'LTC/USD', 'LINK/USD'], index=0)
            quantity = st.number_input("Enter Quantity:", min_value=0.01, step=0.1, format="%.2f", help="Min quantity for LTC/USD and LINK/USD is 1")
            order_type = st.selectbox("Select Order Type:", options=['Buy', 'Sell'], index=0)

            c1 , button, c2 = st.columns([0.5,1,0.5])

            with button:
                st.markdown("")
                # Submit Order Button
                if st.form_submit_button("Submit Order" , type="primary",use_container_width=True):
                    status = alpaca_user.manual_order(symbol, quantity,order_type)
                    # Check buying status
                    if status:
                        st.success("Order submitted successfully!")
                    else:
                        st.error("Insufficient asset. Cannot submit order.")
                st.markdown("")
    
    st.info("The OHLC drawboard is provided by TradingView, intended solely for self-analysis purposes. Please refer the top columns for Alpaca's pricing information", icon="ℹ️")

with st.expander("Analysis Details"):
    
    sent, predicts = st.columns([0.7,0.3])

    with sent:

                st.subheader("Sentiment Analysis Results")
            
                # File paths
                file_path = {
                    'BTC': r'E:/QuantumTrading/QT-API\sentimentData/BTC.csv',
                    'ETH': r'E:/QuantumTrading/QT-API\sentimentData/ETH.csv',
                    'LINK': r'E:/QuantumTrading/QT-API\sentimentData/LINK.csv',
                    'LTC': r'E:/QuantumTrading/QT-API\sentimentData/LTC.csv',
                }

                # Dropdown for selecting cryptocurrency
                selected_crypto = st.selectbox('Select Cryptocurrency', list(file_path.keys()))
                sentiment_result = st.empty()

    with predicts:
                st.markdown("")
                st.subheader("Prediction Analysis Results")
                predict_result = st.empty()

while True:

    # Update real-time data
    alpaca_user.continuousMethods()
    robot_user.updateProfit()

    with sidebarContainer.container():
    
        logs = pd.read_csv("logs.csv")
        logs = logs.tail(5)
        st.markdown("")
        st.dataframe(logs, hide_index=True, use_container_width = True)

    # Fetch real time close prices
    closePrices = alpaca_user.getRealTimePrices()
    
    def get_close_values(close_prices, symbol):
        try:
            current_close = round(close_prices.loc[close_prices['symbol'] == symbol, 'current_close'].values[0], 2)
            last_close = round(close_prices.loc[close_prices['symbol'] == symbol, 'last_close'].values[0], 2)
            return current_close, last_close
        except IndexError:
            # If index is out of bounds, return 0.0 for both values
            return 0.0, 0.0

    # BTC KPI
    btc_current_close, btc_last_close = get_close_values(closePrices, 'btc')
    btc_close = "${:,.2f}".format(btc_current_close)
    delta_btc = round(btc_current_close - btc_last_close, 2)

    # ETH KPI
    eth_current_close, eth_last_close = get_close_values(closePrices, 'eth')
    eth_close = "${:,.2f}".format(eth_current_close)
    delta_eth = round(eth_current_close - eth_last_close, 2)

    # LTC KPI
    ltc_current_close, ltc_last_close = get_close_values(closePrices, 'ltc')
    ltc_close = "${:,.2f}".format(ltc_current_close)
    delta_ltc = round(ltc_current_close - ltc_last_close, 2)

    # LINK KPI
    link_current_close, link_last_close = get_close_values(closePrices, 'link')
    link_close = "${:,.2f}".format(link_current_close)
    delta_link = round(link_current_close - link_last_close, 2)
    
    # Methods for image
    def get_sentiment_image(score):
        if 0 <= score <= 2:
            return pic2
        elif 3 <= score <= 5:
            return pic4
        elif 6 <= score <= 8:
            return pic6
        elif 9 <= score <= 10:
            return pic8
        else:
            # Handle cases outside the specified ranges (optional)
            return None  # or a default image

    def get_ml_image(score):
        if score:
            return up_image
        else:
            return down_image
    
    # Real time KPI 
    with btcPlaceholder.container():

        try:
            btc_sentiment_score = stratergiesClass.check_sentiment('BTC')
            btc_ml_result = stratergiesClass.check_prediction('btc')
        except Exception as e:
            print(f"Error getting BTC sentimen and ml analysis : {e}")

        btc_image1 = get_sentiment_image(btc_sentiment_score)
        btc_image2 = get_ml_image(btc_ml_result)

        btc0, btc1, btc2 = st.columns([0.02, 0.3, 0.9])

        with btc1:
            # Sentiment image
            st.image(btc_image1, width=40, use_column_width=False)
            st.image(btc_image2, width=40, use_column_width=False)

        btc2.metric(
            
                label="Bitcoin",
                value=btc_close,
                delta=delta_btc
            )
        
    with ethPlaceholder.container():

        try:
            eth_sentiment_score = stratergiesClass.check_sentiment('ETH')
            eth_ml_result = stratergiesClass.check_prediction('eth')
        except Exception as e:
            print(f"Error getting ETH sentimen and ml analysis : {e}")

        eth_image1 = get_sentiment_image(eth_sentiment_score)
        eth_image2 = get_ml_image(eth_ml_result)

        eth0, eth1, eth2 = st.columns([0.02, 0.3, 1])

        with eth1:
            # Sentiment image
            st.image(eth_image1, width=40, use_column_width=False)
            st.image(eth_image2, width=40, use_column_width=False)

        eth2.metric(
            
                label="Ethereum",
                value=eth_close,
                delta=delta_eth
            )
        
    with linkPlaceholder.container():

        try:
            link_sentiment_score = stratergiesClass.check_sentiment('LINK')
            link_ml_result = stratergiesClass.check_prediction('link')
        except Exception as e:
            print(f"Error getting LINK sentimen and ml analysis : {e}")

        link_image1 = get_sentiment_image(link_sentiment_score)
        link_image2 = get_ml_image(link_ml_result)

        link0, link1, link2 = st.columns([0.02, 0.4, 1])

        with link1:
            # Sentiment image
            st.image(link_image1, width=40, use_column_width=False)
            st.image(link_image2, width=40, use_column_width=False)

        link2.metric(
            
                label="Chainlink",
                value=link_close,
                delta=delta_link
            )
        
    with ltcPlaceholder.container():

        try:
            ltc_sentiment_score = stratergiesClass.check_sentiment('LTC')
            ltc_ml_result = stratergiesClass.check_prediction('ltc')
        except Exception as e:
            print(f"Error getting LTC sentimen and ml analysis : {e}")

        ltc_image1 = get_sentiment_image(ltc_sentiment_score)
        ltc_image2 = get_ml_image(ltc_ml_result)

        ltc0, ltc1, ltc2 = st.columns([0.02, 0.4, 1])

        with ltc1:
            # Sentiment image
            st.image(ltc_image1, width=40, use_column_width=False)
            st.image(ltc_image2, width=40, use_column_width=False)

        ltc2.metric(
            
                label="Litecoin",
                value=ltc_close,
                delta=delta_ltc
            )
    
    with sentiment_result:

        # Load the selected CSV file
        sent_df = pd.read_csv(file_path[selected_crypto])
        sent_df = sent_df.tail(10)
        st.dataframe(sent_df, hide_index=True, use_container_width = True)
            
    with predict_result:

        # Load the CSV file into a DataFrame
        file_paths = r'E:/QuantumTrading/QT-API/predictionData/prediction.csv'
        df_prediction = pd.read_csv(file_paths)
        st.dataframe(df_prediction, hide_index=True, use_container_width = True)

    # Wait for 10 seconds before the next iteration
    time.sleep(1)