import pandas as pd
import streamlit as st
from alpacas import alpacaClass
import time
from robot import robotClass
import plotly.graph_objects as go
from backtest import backtestClass
from streamlit_extras.app_logo import add_logo

st.set_page_config(layout="wide", initial_sidebar_state="collapsed", page_title="Stratergy Backtest", page_icon = ":money_with_wings:")

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

st.subheader("Robot Backtesting")
st.caption("Ensure to backtest your strategies thoroughly before implementing them in a live trading environment.")

# Create alpaca user
alpaca_user = alpacaClass(username_param)
robot_user = robotClass(username_param)
backtest_user = backtestClass()
max_return_df = pd.DataFrame({
    'symbol': ['BTC/USD', 'ETH/USD', 'LINK/USD', 'LTC/USD',],
    'total_return': [0, 0, 0, 0]  # Initialize with zeros
})
summary_btc = [0,0,0,0,0]
summary_eth = [0,0,0,0,0]
summary_link = [0,0,0,0,0]
summary_ltc = [0,0,0,0,0]

btc_stats = "‎\n\n\n\n\n\n\n\n\n\n\n\n\t\tBacktest a strategy for analytics\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\t\t\t\t\t\t\t\t‎"
eth_stats = "‎\n\n\n\n\n\n\n\n\n\n\n\n\t\tBacktest a strategy for analytics\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\t\t\t\t\t\t\t\t‎"
ltc_stats = "‎\n\n\n\n\n\n\n\n\n\n\n\n\t\tBacktest a strategy for analytics\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\t\t\t\t\t\t\t\t‎"
link_stats = "‎\n\n\n\n\n\n\n\n\n\n\n\n\n\t\tBacktest a strategy for analytics\n\n\n\n\n\n\n\n\n\n\n\n\n\n\t\t\t\t\t\t\t\t‎"

# Use st.columns to create two columns
form_column, view_column = st.columns([0.8,1])

# Store the previous values of start_date and end_date
prev_start_date = "01-01-2023"
prev_end_date = "31-01-2023"

# Form to test stratergy on historical data
with form_column:

    st.markdown("")

    stratContainer = st.container(border=True)

    with stratContainer:
        image_path = "pics\strategies.PNG"
        st.image(image_path)
        st.markdown("")

    with st.form("my_form"):
        start_date = st.text_input("Start Date (DD-MM-YYYY)", key="start_date_input", value=prev_start_date, help="Choose the starting date for the backtesting data period.")
        end_date = st.text_input("End Date (DD-MM-YYYY)", key="end_date_input", value=prev_end_date, help="Choose the end date for the backtesting data period.")
        selected_strategy = st.selectbox("Select Trading Strategy", ["Simple Moving Average", "Moving Average Convergence Divergence", "Relative Strength Index", "MACD RSI Synergy"], help="Choose the stratergy for the backtesting implementation")

        c1 ,  button, c2 , = st.columns([1,1,1])

        with button:

            # Button to fetch historical data
            if st.form_submit_button("Backtest Strategy", type="primary",use_container_width=True):
                    # If date has changed
                    if start_date != prev_start_date or end_date != prev_end_date:
                            
                        bar=st.empty()

                        bar=st.progress(0)
                        robot_user.get_historical_data(start_date, end_date)
                    
                        bar.progress(20)
                        summary_btc, btc_stats = backtest_user.backtest_indv("BTCUSD",start_date,selected_strategy)

                        bar.progress(40)
                        summary_eth, eth_stats = backtest_user.backtest_indv("ETHUSD",start_date,selected_strategy)

                        bar.progress(60)
                        summary_ltc, ltc_stats = backtest_user.backtest_indv("LTCUSD",start_date,selected_strategy)

                        bar.progress(80)
                        summary_link, link_stats = backtest_user.backtest_indv("LINKUSD",start_date,selected_strategy)

                        bar.progress(100)
                        max_return_df = backtest_user.start_backtest(start_date,selected_strategy)

                        bar.empty()

                    else:
                        
                        bar=st.empty()
                    
                        bar=st.progress(20)
                        summary_btc, btc_stats = backtest_user.backtest_indv("BTCUSD",start_date,selected_strategy)

                        bar.progress(40)
                        summary_eth, eth_stats = backtest_user.backtest_indv("ETHUSD",start_date,selected_strategy)

                        bar.progress(60)
                        summary_ltc, ltc_stats = backtest_user.backtest_indv("LTCUSD",start_date,selected_strategy)

                        bar.progress(80)
                        summary_link, link_stats = backtest_user.backtest_indv("LINKUSD",start_date,selected_strategy)

                        bar.progress(100)
                        max_return_df = backtest_user.start_backtest(start_date,selected_strategy)
                        
                        bar.empty()

                    # Update previous values
                    prev_start_date = start_date
                    prev_end_date = end_date
        st.caption("*Backtesting is only applicable to strategies relying on technical analysis.")

    with st.expander("Backtesting Details"):


        tab2, tab3, tab4, tab5 = st.tabs(["BTC/USD Statistics","ETH/USD Statistics","LINK/USD Statistics","LTC/USD Statistics" ])

        
        with tab2:
            st.text(btc_stats)

        with tab3:
            st.text(eth_stats)

        with tab4:
            st.text(ltc_stats)

        with tab5:
            st.text(link_stats)

with view_column:

    st.markdown("")

    c1,c2,c3,c4,c6 = st.columns(5)

    with c1:
        c1Container = st.container(border=True)

        with c1Container:
            max_return_symbol = max_return_df['total_return'].idxmax()
            st.markdown("<p style='text-align: center;font-size: 14px;'>Crypto Won</p>", unsafe_allow_html=True)
            st.subheader(max_return_symbol if max_return_df['total_return'].max() != 0 else "‎")

            if max_return_symbol == 'BTC/USD':
                selected_stats_df = summary_btc
            elif max_return_symbol == 'ETH/USD':
                selected_stats_df = summary_eth
            elif max_return_symbol == 'LTC/USD':
                selected_stats_df = summary_ltc
            elif max_return_symbol == 'LINK/USD':
                selected_stats_df = summary_link
            else:
                selected_stats_df = [0,0,0,0,0]

    with c2:
        c2Container = st.container(border=True)

        with c2Container:
            st.markdown("<p style='text-align: center;font-size: 14px;'>Start Value</p>", unsafe_allow_html=True)
            st.subheader(selected_stats_df[0] if selected_stats_df[0] != 0 else "‎")

    with c3:
        c3Container = st.container(border=True)

        with c3Container:
            st.markdown("<p style='text-align: center;font-size: 14px;'>End Value</p>", unsafe_allow_html=True)
            st.subheader(selected_stats_df[1] if selected_stats_df[1] != 0 else "‎")

    with c4:
        c4Container = st.container(border=True)

        with c4Container:
            st.markdown("<p style='text-align: center;font-size: 14px;'>Total Return</p>", unsafe_allow_html=True)
            st.subheader(selected_stats_df[2] if selected_stats_df[2] != 0 else "‎")

    with c6:
        c5Container = st.container(border=True)

        with c5Container:
            st.markdown("<p style='text-align: center;font-size: 14px;'>Total Trades</p>", unsafe_allow_html=True)
            st.subheader(selected_stats_df[3] if selected_stats_df[3] != 0 else "‎")

    graphContainer = st.container(border=True)

    with graphContainer:

            # Display mean bar chart  
            fig = go.Figure(go.Bar())

            # Check if DataFrame is not empty, then update the figure
            if not max_return_df.empty:
                max_return_df['color'] = ['#8BB276' if val >= 0 else '#F35B65' for val in max_return_df['total_return']]

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
                height=400
            )

            # Show the plot
            st.plotly_chart(fig,use_container_width=True)

            image_path = "pics\pnl.PNG"
            st.image(image_path)
    
    
        
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
    time.sleep(60)

    
    