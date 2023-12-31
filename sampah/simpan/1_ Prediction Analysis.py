import streamlit as st
import datetime
import numpy as np
import plotly.graph_objects as go
from stock import Stock
import numpy as np
import pandas as pd
import yfinance as yf

st.set_page_config(layout="wide", initial_sidebar_state="expanded")
st.title('Detailed Prediction Analysis')

# ------ layout setting---------------------------
window_selection_c = st.container() # create an empty container in the sidebar
# ----------Time window selection-----------------
YESTERDAY=datetime.date.today()-datetime.timedelta(days=1)
YESTERDAY = Stock.nearest_business_day(YESTERDAY) #Round to business day

DEFAULT_START=YESTERDAY - datetime.timedelta(days=700)
DEFAULT_START = Stock.nearest_business_day(DEFAULT_START)

# Set the start and end dates without user input
START = Stock.nearest_business_day(DEFAULT_START)
END = Stock.nearest_business_day(YESTERDAY)

# ---------------stock selection------------------
STOCKS = np.array([ "BTC-USD", "ETH-USD", "BNB-USD",'XRP-USD']) 
SYMB = window_selection_c.selectbox("select stock", STOCKS)

# Initialize the last selected stock to "GOOG"
if "last_selected_stock" not in st.session_state:
    st.session_state.last_selected_stock = "BTC-USD"

#----part-1--------------------------------Session state intializations---------------------------------------------------------------

if "TEST_INTERVAL_LENGTH" not in st.session_state:
    # set the initial default value of test interval
    st.session_state.TEST_INTERVAL_LENGTH = 60

if "TRAIN_INTERVAL_LENGTH" not in st.session_state:
    # set the initial default value of the training length widget
    st.session_state.TRAIN_INTERVAL_LENGTH = 500

if "HORIZON" not in st.session_state:
    # set the initial default value of horizon length widget
    st.session_state.HORIZON = 60
    
#---------------------------------------------------------Train_test_forecast_splits---------------------------------------------------

# Assuming you have some default values for HORIZON, TEST_INTERVAL_LENGTH, and TRAIN_INTERVAL_LENGTH
train_test_forecast_c = st.container()

HORIZON = train_test_forecast_c.number_input(
    "Prediction Period", min_value=7, max_value=200, key="HORIZON"
)

DEFAULT_TEST_INTERVAL_LENGTH = 60
DEFAULT_TRAIN_INTERVAL_LENGTH = 500
# # # ------------------------Plot stock linecharts--------------------

# Declare stock outside the if block to make it accessible later
stock = Stock(SYMB)
#used in all tabs

# Generate and display the figure for the initialized GOOG
fig = go.Figure()
stock = Stock(symbol=SYMB)

#graph tiny numbers tu
# change_c = st.container()
# with change_c:
#     stock.show_delta()
#Load historical data based on last selected stock
stock.load_data(st.session_state.last_selected_stock,START, END, inplace=True)

fig = stock.plot_raw_data(fig)

fig.update_layout(
    width= 1100,
    margin=dict(l=0, r=0, t=0, b=0, pad=0),
    legend=dict(
        x=0,
        y=0.99,
        traceorder="normal",
        font=dict(size=12),
    ),
    autosize=False,
    template="plotly_dark",
)

st.write(fig)


# Check if the selected stock has changed and RESET EVERYTHING (except cache)
if st.session_state.last_selected_stock != SYMB:
    # Update the last selected stock
    st.session_state.TRAIN_JOB = False
    st.session_state.TRAIN_JOB_CLICKED = False
    st.session_state.last_selected_stock = SYMB
    



#---------------------------------------------------------Prediction Report---------------------------------------------------


# Initialize TRAIN_JOB to False
if 'TRAIN_JOB' not in st.session_state:
    st.session_state.TRAIN_JOB = False

# Initialize CLICKED to False
if 'CLICKED' not in st.session_state:
    st.session_state.CLICKED = False

# Print result
if st.session_state.TRAIN_JOB:
    
    text=st.empty() # Because streamlit adds widgets sequentially, we have to reserve a place at the top (after the chart of part 1)
    bar=st.empty() # Reserve a place for a progess bar
    
    text.write('Training model ... ') 
    bar=st.progress(0)

    stock = Stock(SYMB) 
    bar.progress(10)
    TEST_INTERVAL_LENGTH=st.session_state.TEST_INTERVAL_LENGTH #Retrieve input from the user
    TRAIN_INTERVAL_LENGTH=st.session_state.TRAIN_INTERVAL_LENGTH

    stock.load_train_test_data(TEST_INTERVAL_LENGTH, TRAIN_INTERVAL_LENGTH) #load train test data into the stock object, it's using cache
    bar.progress(30)
    stock.train_prophet() #this is also using cache
    bar.progress(70)
    text.write('Plotting test results ...')
    fig = stock.plot_test()
    bar.progress(100)
    bar.empty() #Turn the progress bar object back to what it was before and empty container
    st.markdown(
        f"## {SYMB} stock forecasts on testing set, Testing error {round(stock.test_mape*100,2)}%"
    )
    st.plotly_chart(fig)
    text.write('Generating forecasts ... ')
    fig2=stock.plot_inference() #Generate forecasts and plot them (no cache but figures are not updated if their data didn't change)
    st.markdown(f'## Forecasts for the next {st.session_state.HORIZON} days')
    st.plotly_chart(fig2)
    text.empty()

    if st.session_state.CLICKED:
        st.session_state.TRAIN_JOB = False

else:
    st.markdown('Setup training job and hit Train')
    # Show the Train button 
    if train_test_forecast_c.button('Predict', key='PredictButton'): 
        st.session_state.TRAIN_JOB = True
        st.session_state.CLICKED = True
