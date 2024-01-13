import pandas as pd
import streamlit as st
from alpacas import alpacaClass
from robot import robotClass
import time
import plotly.graph_objects as go
from streamlit_extras.app_logo import add_logo

st.set_page_config(layout="wide", initial_sidebar_state="collapsed",page_title="Profile Details", page_icon = ":money_with_wings:")

# Get parameter from link for auth
username_param = st.experimental_get_query_params().get("id", [""])[0]

add_logo("pics/logo.png")

with st.sidebar:

    sidebarContainer = st.empty()

    st.markdown("")
    st.markdown("")

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



# Create alpaca user
alpaca_user = alpacaClass(username_param)
robot_user = robotClass(username_param)

# Use st.columns to create two columns
left , profile_column, right = st.columns([1,1,1])


############################## column create and update on the right

# Form to create a robot
with profile_column:

    st.markdown("<h3 style='text-align:center'>Profile Detail</h3>", unsafe_allow_html=True)

    with st.form("update_form"):

        st.markdown("")
        # Input field for username
        username_value = st.text_input("Username", value=alpaca_user.username, key="username", disabled=True)

        # Input field for password
        password_value = st.text_input("Password", value=alpaca_user.password, type="password", key="password", disabled=False)

        # Input field for API key
        api_key_value = st.text_input("API Key", value=alpaca_user.api_key, key="api_key", disabled=False)

        # Input field for secret key
        secret_key_value = st.text_input("Secret Key", value=alpaca_user.secret_key, key="secret_key", disabled=False)

        st.markdown("")

        c1 , button, c2 = st.columns([1,1,1])

        with button:
            if st.form_submit_button("Update" , type="primary", use_container_width=True):
                if alpaca_user.update_user_details(password=password_value, api_key=api_key_value, secret_key=secret_key_value):
                    st.success("User details updated successfully!")
                else:
                    st.error("Failed to update user details.")

# Loop to fetch current minute's data every 10 seconds
while True:

    with sidebarContainer.container():
    
        logs = pd.read_csv("logs.csv")
        logs = logs.tail(3)
        st.markdown("")
        st.dataframe(logs, hide_index=True, use_container_width = True)

    # Update real-time data
    alpaca_user.continuousMethods()
    robot_user.updateProfit()
        
    # Wait for 10 seconds before the next iteration
    time.sleep(60)

    
    