import altair as alt
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
from datetime import datetime
from alpacas import alpacaClass
from robot import robotClass
import pytz
from PIL import Image

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

############################################# Real time Dashboard #####################################

# Dashboard title
st.title('REAL-TIME CANDLESTICK CHART')

# Create alpaca user
alpaca_user = alpacaClass()
robot_user = robotClass()

# creating a single-element container
placeholder = st.empty()

# Loop to fetch current minute's data every 10 seconds
while True:

    # Update real-time data
    alpaca_user.continuousMethods()
    robot_user.updateProfit()

    # Fetch real-time data
    alpaca_user.fetch_real_time_btc_data()
    live_data = alpaca_user.get_live_btc_data()

    with placeholder.container():

        # Timer

        # Set the time zone to Malaysia (UTC+8)
        malaysia_timezone = pytz.timezone('Asia/Kuala_Lumpur')

        # Get the current time
        current_time_utc = datetime.utcnow()

        # Convert UTC time to Malaysia time
        current_time_malaysia = current_time_utc.replace(tzinfo=pytz.utc).astimezone(malaysia_timezone)

        # Format the time for display
        formatted_time = current_time_malaysia.strftime("%Y-%m-%d %H:%M:%S")

        st.markdown(f"Last update: {formatted_time}")


        crypto, kpi_open, kpi_high, kpi_low, kpi_close = st.columns(5)

        with crypto:

            cryptoContainer = st.container(border=True)

            with cryptoContainer:

                st.markdown("")
                
                btc1, btc2 = st.columns([0.4, 1])

                with btc1:
                    btc_image = Image.open("pics/btc.png")
                    st.image(btc_image, width=62, use_column_width=False)
                    st.markdown("")

                with btc2:
                    # Sidebar dropdown
                    # List of crypto options
                    crypto_options = ["BTC/USD", "DOT/USD", "ETH/USD", "LINK/USD", "LTC/USD"]

                    # Create a dropdown in the Streamlit sidebar
                    # selected_crypto = btc2.selectbox("Cryptocurrency", crypto_options)
                    
                
        # fill in those three columns with respective metrics or KPIs
        with kpi_open:

            openContainer = st.container(border=True) 

            openContainer.metric(
                label="Open",
                value=live_data['open'].iloc[-1],
                delta=live_data['open'].iloc[-1] - live_data['open'].iloc[-2],
            )

        with kpi_high:

            highContainer = st.container(border=True)

            highContainer.metric(
                label="High",
                value=live_data['high'].iloc[-1],
                delta=live_data['high'].iloc[-1] - live_data['high'].iloc[-2],
            ) 

        with kpi_low:

            lowContainer = st.container(border=True)
        
            lowContainer.metric(
                label="Low",
                value=live_data['low'].iloc[-1],
                delta=live_data['low'].iloc[-1] - live_data['low'].iloc[-2],
            )

        with kpi_close:
            
            closeContainer = st.container(border=True)

            closeContainer.metric(
                label="Close",
                value=live_data['close'].iloc[-1],
                delta=live_data['close'].iloc[-1] - live_data['close'].iloc[-2],
            )       
        
        fig = go.Figure()
        fig = make_subplots(rows=1, cols=1)
        fig.add_trace(go.Candlestick(x=live_data.index, open=live_data.open, high=live_data.high, low=live_data.low, close=live_data.close))
        fig.update_layout(xaxis_title="Date", yaxis_title="Price", width=1300, height=500, template="plotly_dark")
        st.plotly_chart(fig)

        # Wait for 10 seconds before the next iteration
        st.markdown("### Detailed Data View")
        st.table(live_data)
    
        # Wait for 10 seconds before the next iteration
        time.sleep(1)