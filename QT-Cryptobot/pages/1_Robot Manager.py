import pandas as pd
import streamlit as st
from alpacas import alpacaClass
from robot import robotClass
import time
import plotly.graph_objects as go

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

st.title("Robot Manager")

# Create alpaca user
alpaca_user = alpacaClass()
robot_user = robotClass()

# Use st.columns to create two columns
view_column, form_column = st.columns([1,0.5])

# creating a single-element container
placeholder = st.empty()

# Read data from 'robots.csv'
data = alpaca_user.fetch_all_robot()

############################## column create and update on the right

# Form to create a robot
with form_column:


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

                    # Dropdown for new Symbol
                    symbol_options = ["BTC/USD", "DOT/USD", "ETH/USD", "LINK/USD", "LTC/USD"]
                    new_symbol = st.selectbox('Symbol', symbol_options, index=symbol_options.index(default_values['Symbol']))

                    new_quantity = st.number_input('Quantity', value=float(default_values['Quantity']))

                    # Dropdown for new Strategy
                    strategy_options = ["MACD&RSI", "MA&BOL", "RSI", "MACD", "Stochastic"]
                    new_strategy = st.selectbox('Strategy', strategy_options, index=strategy_options.index(default_values['Stratergy']))

                    new_status = st.selectbox('Status', ['Running', 'Stopped'], index=0 if default_values['Status'] == 'Running' else 1)


                    updateButton, deleteButton = st.columns(2)

                    with updateButton:

                        # Update button
                        if st.button('Update Robot'):
                            # Check if a robot with the same parameters already exists
                            existing_data = data[data['Robot Name'] != selected_robot]  # Exclude the selected robot from the check
                            if ((existing_data['Symbol'] == new_symbol) &
                                (existing_data['Stratergy'] == new_strategy)).any():
                                st.error('Error: Robot with the same parameters already exists.')
                            else:
                                # Update the data
                                data.loc[data['Robot Name'] == selected_robot, 'Quantity'] = new_quantity
                                data.loc[data['Robot Name'] == selected_robot, 'Symbol'] = new_symbol
                                data.loc[data['Robot Name'] == selected_robot, 'Stratergy'] = new_strategy
                                data.loc[data['Robot Name'] == selected_robot, 'Status'] = new_status

                                # Save the updated data to the CSV file
                                data.to_csv('Data/robots.csv', index=False)

                                st.success(f'{selected_robot} details updated successfully!')
                    
                    with deleteButton:
                        # Delete button
                        if st.button('Delete Robot'):
                            # Delete the selected robot's row
                            data = data[data['Robot Name'] != selected_robot]
                            # Save the updated data to the CSV file
                            data.to_csv('Data/robots.csv', index=False)
                            st.success(f'{selected_robot} deleted successfully!')

                else:
                    st.warning('No data available for the selected robot.')

        # Create robot data
        with create:

            with st.form("create_form"):
            
                robot_name = st.text_input("Robot Name", key="robot_name_input", value="robot1")

                # Dropdown for Symbol
                symbol_options = ["BTC/USD", "DOT/USD", "ETH/USD", "LINK/USD", "LTC/USD"]
                symb = st.selectbox("Symbol", symbol_options, key="symbol_input", index=0)

                quantity = st.number_input("Quantity", key="quantity_input", value=0.03)

                strategies = ["MACD&RSI", "MA&BOL", "RSI", "MACD", "Stochastic"]
                strategy = st.selectbox("Strategy", strategies, key="strategy_input")

                # Dropdown for Status
                status_options = ["Stopped","Running"]
                status = st.selectbox("Status", status_options, key="status_input", index=0)


                # Create button to trigger data fetching and CSV insertion
                if st.form_submit_button("Create Robot"):
                    # Call the function in alpaca.py to fetch data and insert into CSV
                    created_successfully = robot_user.create_robot(symb, quantity, robot_name, strategy, status)

                    if created_successfully:
                        st.success("Robot created successfully!")
                    else:
                        st.error("Error: Robot already exists.")

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

    # View profit placeholder
    with placeholderViewProfit.container():

        # Read CSV
        df = pd.read_csv("Data/profit.csv")

        # Convert Timestamp to datetime
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])

        # Create figure
        fig = go.Figure()

        # Add a line for each robot
        for robot_name, robot_data in df.groupby('Robot Name'):
            fig.add_trace(go.Scatter(x=robot_data['Timestamp'], y=robot_data['Profit'], mode='lines', name=robot_name))

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

        view_robot_data = pd.read_csv('Data/robots.csv')
        selected_data = view_robot_data.drop(columns=view_robot_data.columns.difference(['Robot Name','Symbol', 'Quantity', 'Stratergy', 'Status']))
        st.table(selected_data)

        st.info('Only one robot can perform one stratergy to one cryptocurrency', icon="ℹ️")

    # View transaction placeholder
    with placeholder.container():

        # Read data from 'robots.csv'
        transaction_data = pd.read_csv('Data/transactions.csv')
        last_5_transactions = transaction_data.tail(5)

        st.subheader("Latest Transactions")
        st.table(last_5_transactions)

        # Wait for 10 seconds before the next iteration
        time.sleep(1)

    
    