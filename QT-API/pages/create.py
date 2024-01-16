import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import requests
import re
from passlib.hash import pbkdf2_sha256  # For password hashing

st.set_page_config(initial_sidebar_state="collapsed")

st.markdown(
    """
<style>
    [data-testid="collapsedControl"] {
        display: none
    }
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
    <style>
    button[kind="secondary"] {
        background: none!important;
        border: none;
        padding: 1!important;
        color: white !important;
        text-decoration: none;
        cursor: pointer;
        border: none !important;
    }
    button[kind="secondary"]:hover {
        text-decoration: none;
        color: red !important;
    }
    button[kind="secondary"]:focus {
        outline: none !important;
        box-shadow: none !important;
        color: red !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Function to validate email format using regex
def is_valid_email(email):
    email_regex = r'^[\w\.-]+@[a-zA-Z\d\.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

# Function to hash passwords using passli
def hash_password(password):
    return pbkdf2_sha256.hash(password)

cc, mid, ccc = st.columns([0.3,1,0.3])

with mid:

    st.markdown("<h2 style='text-align:center'>Create an account</h2>", unsafe_allow_html=True)

    st.write("You need to create account with Alpaca and get your keys [here](https://alpaca.markets/learn/connect-to-alpaca-api/)")

    # Use st.form to create the form
    with st.form("create_user_form"):

        
        # Input fields in the form
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        api_key = st.text_input("Alpaca Key")
        secret_key = st.text_input("Alpaca Secret Key", type="password")

        c1 ,  button, c2 , = st.columns([1,1,1])

        with button:
            # Submit button inside the form
            submitted = st.form_submit_button("Sign up", type = "primary",use_container_width=True)
            st.caption("")

    # Check if the form is submitted
    if submitted:

        # Validate email format
        if not is_valid_email(email):
            st.error("Invalid email format")
        # Check for non-empty values
        if not all([username, email, password, confirm_password, api_key, secret_key]):
            st.error("All fields are required")
        if password != confirm_password:
            st.error("Passwords do not match")
        else:
            password = hash_password(password)

        # Create user using FastAPI route
        new_user_data = {"username": username, "email": email, "password": password, "api_key": api_key, "secret_key": secret_key}
        response = requests.post("http://127.0.0.1:8000/user/create", json=new_user_data, timeout=30)

        if response.status_code == 201:
            st.success("User created successfully!")
        elif response.status_code == 409:
            st.error("Username already exists. Please choose a different username.")
        else:
            st.error(f"Failed to create user. Status code: {response.status_code}")

    if st.button("Already have an account?  Login"):
            switch_page("login")
