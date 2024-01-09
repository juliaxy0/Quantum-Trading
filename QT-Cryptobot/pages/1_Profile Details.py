import pandas as pd
import streamlit as st
from alpacas import alpacaClass
from robot import robotClass
import time
import plotly.graph_objects as go
from streamlit_extras.app_logo import add_logo

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

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

st.subheader("Profile Detail")

# Create alpaca user
alpaca_user = alpacaClass(username_param)
robot_user = robotClass(username_param)

# Use st.columns to create two columns
profile_column, transaction_column = st.columns([0.5,1])


############################## column create and update on the right

# Form to create a robot
with profile_column:

    profileContainer = st.container(border=True)

    with profileContainer:

        with st.form("update_form"):
            # Input field for username
            username_value = st.text_input("Username", value=alpaca_user.username, key="username", disabled=True)

            # Input field for password
            password_value = st.text_input("Password", value=alpaca_user.password, type="password", key="password", disabled=False)

            # Input field for API key
            api_key_value = st.text_input("API Key", value=alpaca_user.api_key, key="api_key", disabled=False)

            # Input field for secret key
            secret_key_value = st.text_input("Secret Key", value=alpaca_user.secret_key, key="secret_key", disabled=False)

            if st.form_submit_button("Update" , type="primary"):
                if alpaca_user.update_user_details(password=password_value, api_key=api_key_value, secret_key=secret_key_value):
                    st.success("User details updated successfully!")
                else:
                    st.error("Failed to update user details.")

with transaction_column:

    transactionContainer = st.container(border=True)

    with transactionContainer:

        # Read CSV
        df = robot_user.get_transaction()

        # Remove the 'Username' column
        df = df.drop(columns=['Username'])

        # Create a sidebar with a dropdown for selecting the robot name
        selected_robot_name = st.selectbox('Select Robot Name', df['Robot Name'].unique())

        # Filter transactions based on the selected robot name
        filtered_df = df[df['Robot Name'] == selected_robot_name]

        # Display the transactions in a table
        st.table(filtered_df)

# Loop to fetch current minute's data every 10 seconds
while True:

    with sidebarContainer.container():
    
        logs = pd.read_csv("logs.csv")
        logs = logs.tail(5)
        st.markdown("")
        st.dataframe(logs, hide_index=True, use_container_width = True)

    # Update real-time data
    alpaca_user.continuousMethods()
    robot_user.updateProfit()
        
    # Wait for 10 seconds before the next iteration
    time.sleep(1)

    
    