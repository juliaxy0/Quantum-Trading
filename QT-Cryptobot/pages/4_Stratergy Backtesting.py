import pandas as pd
import streamlit as st
from alpacas import alpacaClass
import time
import pandas as pd
from robot import robotClass
import plotly.graph_objects as go
from backtest import backtestClass
from streamlit_extras.app_logo import add_logo

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# Get parameter from link for auth
username_param = st.experimental_get_query_params().get("username", [""])[0]

add_logo("pics/logo.png")

# st.markdown(
#     """
#     <style>
#     button {
#         background: none!important;
#         border: none;
#         padding: 0!important;
#         color: grey !important;
#         text-decoration: none;
#         cursor: pointer;
#         border: none !important;
#     }
#     button:hover {
#         text-decoration: none;
#         color: black !important;
#     }
#     button:focus {
#         outline: none !important;
#         box-shadow: none !important;
#         color: black !important;
#     }
#     </style>
#     """,
#     unsafe_allow_html=True,
# )

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

st.subheader("Robot Backtesting")

# Create alpaca user
alpaca_user = alpacaClass(username_param)
robot_user = robotClass(username_param)
backtest_user = backtestClass()

# Empty df
max_return_df = pd.DataFrame()
btc_stats = " "
eth_stats = " "
ltc_stats = " "
link_stats = " "

# Use st.columns to create two columns
form_column, view_column = st.columns([1,0.8])

# Store the previous values of start_date and end_date
prev_start_date = "01-01-2023"
prev_end_date = "31-01-2023"

# Form to test stratergy on historical data
with form_column:

    st.markdown("")

    with st.form("my_form"):
        start_date = st.text_input("Start Date (DD-MM-YYYY)", key="start_date_input", value=prev_start_date)
        end_date = st.text_input("End Date (DD-MM-YYYY)", key="end_date_input", value=prev_end_date)
        selected_strategy = st.selectbox("Select Trading Strategy", ["SMA", "MACD", "RSI", "BB"])

        # Button to fetch historical data
        if st.form_submit_button("Backtest Strategy", type="primary"):
                # If date has changed
                if start_date != prev_start_date or end_date != prev_end_date:
                        
                    text=st.empty()
                    bar=st.empty()

                    text.write('Updating backtesting data... ') 
                    bar=st.progress(0)
                    robot_user.get_historical_data(start_date, end_date)
                
                    text.write('Backtesting on BTC/USD... ') 
                    bar.progress(20)
                    btc_stats = backtest_user.backtest_indv("BTCUSD",start_date,selected_strategy)

                    text.write('Backtesting on ETH/USD... ') 
                    bar.progress(40)
                    eth_stats = backtest_user.backtest_indv("ETHUSD",start_date,selected_strategy)

                    text.write('Backtesting on LTC/USD... ') 
                    bar.progress(60)
                    ltc_stats = backtest_user.backtest_indv("LTCUSD",start_date,selected_strategy)

                    text.write('Backtesting on LINK/USD... ') 
                    bar.progress(80)
                    link_stats = backtest_user.backtest_indv("LINKUSD",start_date,selected_strategy)

                    text.write('Comparing cryto... ') 
                    bar.progress(100)
                    max_return_df = backtest_user.start_backtest(start_date,selected_strategy)

                    bar.empty()
                    text.empty()

                else:
                    
                    text=st.empty()
                    bar=st.empty()
                
                    text.write('Backtesting on BTC/USD... ') 
                    bar=st.progress(20)
                    btc_stats = backtest_user.backtest_indv("BTCUSD",start_date,selected_strategy)

                    text.write('Backtesting on ETH/USD... ') 
                    bar.progress(40)
                    eth_stats = backtest_user.backtest_indv("ETHUSD",start_date,selected_strategy)

                    text.write('Backtesting on LTC/USD... ') 
                    bar.progress(60)
                    ltc_stats = backtest_user.backtest_indv("LTCUSD",start_date,selected_strategy)

                    text.write('Backtesting on LINK/USD... ') 
                    bar.progress(80)
                    link_stats = backtest_user.backtest_indv("LINKUSD",start_date,selected_strategy)

                    text.write('Comparing cryto... ') 
                    bar.progress(100)
                    max_return_df = backtest_user.start_backtest(start_date,selected_strategy)
                    
                    bar.empty()
                    text.empty()

                # Update previous values
                prev_start_date = start_date
                prev_end_date = end_date
        st.caption("*Backtesting is only applicable to strategies relying on technical analysis.")

    graphContainer = st.container(border=True)

    with graphContainer:

            # Display mean bar chart  
            fig = go.Figure(go.Bar())

            # Check if DataFrame is not empty, then update the figure
            if not max_return_df.empty:
                max_return_df['color'] = ['green' if val >= 0 else 'red' for val in max_return_df['total_return']]

                fig.add_trace(go.Bar(
                    x=max_return_df.index,
                    y=max_return_df['total_return'],
                    marker_color=max_return_df['color'],  # You can customize the colors here
                ))

            # Update layout
            fig.update_layout(
                title='Mean Return by Symbol',
                xaxis=dict(title='Symbol'),
                yaxis=dict(title='Mean Return'),
                height=300
            )

            # Show the plot
            st.plotly_chart(fig,use_container_width=True)

    

with view_column:

    st.markdown("")

    meanContainer = st.container(border=True)

    with meanContainer:

        tab2, tab3, tab4, tab5 = st.tabs(["BTC/USD Statistics","ETH/USD Statistics","LINK/USD Statistics","LTC/USD Statistics" ])

        
        with tab2:
            st.text(btc_stats)

        with tab3:
            st.text(eth_stats)

        with tab4:
            st.text(ltc_stats)


        with tab5:
            st.text(link_stats)
        
# Loop to fetch current minute's data every 10 seconds
while True:

    # Update real-time data
    alpaca_user.continuousMethods()
    robot_user.updateProfit()

    with sidebarContainer.container():
    
        logs = pd.read_csv("logs.csv")
        logs = logs.tail(5)
        st.markdown("")
        st.dataframe(logs, hide_index=True, use_container_width = True)

    # Wait for 10 seconds before the next iteration
    time.sleep(1)

    
    