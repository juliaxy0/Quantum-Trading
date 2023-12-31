import pandas as pd
import streamlit as st
from alpacas import alpacaClass
import time
import pandas as pd
from robot import robotClass
import plotly.graph_objects as go

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

st.subheader("Robot Backtesting")

# Create alpaca user
alpaca_user = alpacaClass()
robot_user = robotClass()

# Empty df
mean_return_df = pd.DataFrame()

# Use st.columns to create two columns
form_column, view_column = st.columns([0.6,1])

# Store the previous values of start_date and end_date
prev_start_date = "01-01-2023"
prev_end_date = "31-01-2023"

# Form to test stratergy on historical data
with form_column:

    st.markdown("")

    with st.form("my_form"):
        st.subheader("Select backtesting details")
        start_date = st.text_input("Start Date (DD-MM-YYYY)", key="start_date_input", value=prev_start_date)
        end_date = st.text_input("End Date (DD-MM-YYYY)", key="end_date_input", value=prev_end_date)
        selected_strategy = st.selectbox("Select Trading Strategy", ["SMA", "MACD", "RSI", "BB"])
        include_sentiment = st.checkbox("Include Sentiment Analysis")
        include_prediction = st.checkbox("Include Price Prediction")

        # Button to fetch historical data
        if st.form_submit_button("Fetch historical data"):
                # If date has changed
                if start_date != prev_start_date or end_date != prev_end_date:
                    with st.spinner("Updating backtesting historical data..."):
                        robot_user.get_historical_data(start_date, end_date)
                    with st.spinner("Backtesting data on all crypto..."):
                        # mean_return_df = robot_user.start_backtest()
                        print()
                else:
                    with st.spinner("Backtesting data on all crypto..."):
                        # mean_return_df = robot_user.start_backtest()
                        print()

                # Update previous values
                prev_start_date = start_date
                prev_end_date = end_date

                st.success("Backtesting Completed!")
        st.caption("*Backtesting is only applicable to strategies relying on technical analysis.")

with view_column:

    st.markdown("")

    meanContainer = st.container(border=True)

    with meanContainer:

        # Display mean bar chart  
        fig = go.Figure(go.Bar())

        # Check if DataFrame is not empty, then update the figure
        if not mean_return_df.empty:
            mean_return_df['color'] = ['green' if val >= 0 else 'red' for val in mean_return_df['total_return']]

            fig.add_trace(go.Bar(
                x=mean_return_df.index,
                y=mean_return_df['total_return'],
                marker_color=mean_return_df['color'],  # You can customize the colors here
            ))

        # Update layout
        fig.update_layout(
            title='Mean Return by Symbol',
            xaxis=dict(title='Symbol'),
            yaxis=dict(title='Mean Return'),
        )

        # Show the plot
        st.plotly_chart(fig,use_container_width=True, height=1700)


btc, eth, link, ltc = st.columns(4)

with btc:

    btcContainer = st.container(border=True)

    with btcContainer:

        st.markdown(" ")

with eth:

    ethContainer = st.container(border=True)

    with ethContainer:

        st.markdown(" ")

with link:

    linkContainer = st.container(border=True)

    with linkContainer:

        st.markdown(" ")

with ltc:

    linkContainer = st.container(border=True)

    with linkContainer:

        st.markdown(" ")

        
# Loop to fetch current minute's data every 10 seconds
while True:

    # Update real-time data
    alpaca_user.continuousMethods()
    robot_user.updateProfit()

    # Wait for 10 seconds before the next iteration
    time.sleep(1)

    
    