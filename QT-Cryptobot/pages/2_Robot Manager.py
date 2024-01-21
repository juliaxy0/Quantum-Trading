import pandas as pd
import streamlit as st
from alpacas import alpacaClass
from robot import robotClass
import time
import plotly.graph_objects as go
from streamlit_extras.app_logo import add_logo

st.set_page_config(layout="wide", initial_sidebar_state="collapsed",page_title="Robot Manager", page_icon = ":money_with_wings:")

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

st.subheader("Robot Manager")
st.caption("Effectively oversee your automated trading robots and monitor their performance and profitability in this page.")

# Create alpaca user
alpaca_user = alpacaClass(username_param)
robot_user = robotClass(username_param)

# Use st.columns to create two columns
view_column, form_column = st.columns([1,0.5])

# Read data from 'robots.csv'
data = alpaca_user.fetch_all_robot()

############################## column create and update on the right

# Form to create a robot
with form_column:

        # TODO: add these to robot
        # include_sentiment = st.checkbox("Include Sentiment Analysis")
        # include_prediction = st.checkbox("Include Price Prediction")

    formContainer = st.container(border=True)

    with formContainer:

        update, create   = st.tabs(["Update Robot","Create Robot"])
        
        # Update robot data
        with update:

            updateContainer = st.container(border=True)

            with updateContainer:

                # Dropdown to choose Robot Name
                selected_robot = st.selectbox('Robot Name', data['Robot Name'].unique())

                # Filter data for the selected robot
                selected_robot_data = data[data['Robot Name'] == selected_robot]

                # Get default values from the selected row
                default_values = selected_robot_data.iloc[0] if not selected_robot_data.empty else None

                if not selected_robot_data.empty:

                    # Uneditable Symbol
                    new_symbol = st.text_input('Symbol', value=default_values['Symbol'], key='symbol', disabled=True)
                    
                    new_quantity = st.number_input('Quantity', value=float(default_values['Quantity']))

                    # Dropdown for new Strategy
                    strategy_options = ["MACD RSI Synergy", "Relative Strength Index", "Moving Average Convergence Divergence", "Simple Moving Average"]
                    new_strategy = st.selectbox('Strategy', strategy_options, index=strategy_options.index(default_values['Strategy']))

                    new_status = st.selectbox('Status', ['Running', 'Stopped'], index=0 if default_values['Status'] == 'Running' else 1)

                    # Checkbox for Sentiment Analysis
                    new_sentiment_analysis = st.checkbox("Include Sentiment Analysis", value=default_values['Sentiment'])

                    # Checkbox for Prediction Analysis
                    new_prediction_analysis = st.checkbox("Include Prediction Analysis", value=default_values['Prediction'])

                    st.caption("")

                    c1, updateButton, c2, deleteButton, c3 = st.columns([0.1,0.5,0.1,0.5,0.1])

                    with updateButton:

                        # Update button
                        if st.button('Update Robot', type="primary" ,use_container_width=True):
                            # Check if a robot with the same parameters already exists
                            existing_data = data[data['Robot Name'] != selected_robot]  # Exclude the selected robot from the check
                            if ((existing_data['Symbol'] == new_symbol) &
                                (existing_data['Strategy'] == new_strategy)).any():
                                st.error('Error: Robot with the same parameters already exists.')
                            else:
                                robot_user.updateRobot(data, selected_robot, new_quantity, new_strategy, new_status, new_sentiment_analysis, new_prediction_analysis)
                                st.rerun()
                    
                    with deleteButton:
                        # Delete button
                        if st.button('Delete Robot', type="primary", use_container_width=True):
                            robot_user.deleteRobot(data, selected_robot)
                            st.rerun()

                else:
                    st.warning('No data available for the selected robot.')

        # Create robot data
        with create:

            with st.form("create_form"):
            
                robot_name = st.text_input("Robot Name", key="robot_name_input", value="robot1")

                # Dropdown for Symbol
                symbol_options = ["BTC/USD", "ETH/USD", "LINK/USD", "LTC/USD"]
                symb = st.selectbox("Symbol", symbol_options, key="symbol_input", index=0)

                quantity = st.number_input("Quantity", key="quantity_input", value=0.03)

                strategies = ["MACD RSI Synergy", "Relative Strength Index", "Moving Average Convergence Divergence", "Simple Moving Average"]
                strategy = st.selectbox("Strategy", strategies, key="strategy_input")

                # Dropdown for Status
                status_options = ["Stopped","Running"]
                status = st.selectbox("Status", status_options, key="status_input", index=0)
                

                sentiment_analysis = st.checkbox("Include Sentiment Analysis")
                prediction_analysis = st.checkbox("Include Prediction Analysis")

                st.caption("")

                l1, buttons, l2 = st.columns([1,1,1])

                with buttons:
                    st.markdown("")
                    # Create button to trigger data fetching and CSV insertion
                    if st.form_submit_button("Create Robot" , type="primary" ,use_container_width=True):
                        # Call the function in alpaca.py to fetch data and insert into CSV
                        created_successfully = robot_user.create_robot(symb, quantity, robot_name, strategy, sentiment_analysis, prediction_analysis, status)

                        if created_successfully:
                            st.success("Robot created successfully!")
                            st.rerun()
                        else:
                            
                            st.error("Error: Robot already exists.")

        st.caption("*A single robot is limited to implementing just one strategy for a particular cryptocurrency.")

############################## column view on the left

# View robots column

with view_column:

    viewProfitContainer = st.container(border=True)

    with viewProfitContainer:

        placeholderViewProfit = st.empty()       

        placeholderViewRobot = st.empty()


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

    # View profit placeholder
    with placeholderViewProfit.container():
        # Read CSV
        df = robot_user.get_profit()
        df = df.tail(100)
        
        # Convert Timestamp to datetime
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])

        # Create figure
        fig = go.Figure()

        # Iterate over unique combinations of Username and Robot Name
        # Iterate over unique combinations of Username and Robot Name
        for (username, robot_name), robot_data in df.groupby(['Username', 'Robot Name']):
            fig.add_trace(go.Scatter(x=robot_data['Timestamp'], y=robot_data['Profit'], mode='lines', name=f"{robot_name}"))


        # Update layout with custom width and height
        fig.update_layout(
            title='Profit for Each Robot',
            xaxis_title='Timestamp',
            yaxis_title='Profit',
            width=850,  # Set custom width
            height=305  # Set custom height
        )

        # Display the graph using Streamlit
        st.plotly_chart(fig)
        
    # View robot placeholder
    with placeholderViewRobot.container():

        view_robot_data = alpaca_user.fetch_all_robot()
        selected_data = view_robot_data.drop(columns=view_robot_data.columns.difference(['Robot Name','Symbol', 'Quantity', 'Strategy', 'Sentiment', 'Prediction', 'Status','Bought']))
        st.dataframe(selected_data,hide_index=True, use_container_width = True)

        st.info('Backtest robot with stratergies for more informed decisions', icon="ℹ️")

        # Wait for 10 seconds before the next iteration
        time.sleep(1)

    
    