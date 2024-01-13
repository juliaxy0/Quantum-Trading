import streamlit as st
from pymongo import MongoClient
from passlib.hash import pbkdf2_sha256  # For password hashing
import re


st.set_page_config(layout="wide")

# Initialize MongoDB connection.
@st.cache_resource
def init_connection():
    return MongoClient("mongodb+srv://root:PlwvHQRnWEoYW11e@trade.qdxypz1.mongodb.net/?retryWrites=true&w=majority")

client = init_connection()
db = client.User
users_collection = db.users

# Function to hash passwords using passli
def hash_password(password):
    return pbkdf2_sha256.hash(password)

# Function to verify hashed password
def verify_password(input_password, hashed_password):
    return pbkdf2_sha256.verify(input_password, hashed_password)

# Function to validate email format using regex
def is_valid_email(email):
    email_regex = r'^[\w\.-]+@[a-zA-Z\d\.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

# Function to display logout button and clear session state
def logout():
    username = st.session_state.username
    logout_button = st.sidebar.button(f"Log Out {username}", key=f"logout_button_{username}", on_click=clear_session)

def clear_session():
    st.session_state.form = ""
    st.session_state.username = ""
    st.session_state.predictions = ""
    st.success("Logged out successfully")

def signup():
    st.header("Sign Up")
    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    alpaca_key = st.text_input("Alpaca Key")
    alpaca_secret_key = st.text_input("Alpaca Secret Key", type="password")

    if st.button("Sign Up"):
        # Validate email format
        if not is_valid_email(email):
            st.error("Invalid email format")
            return
        # Check for non-empty values
        if not all([username, email, password, confirm_password, alpaca_key, alpaca_secret_key]):
            st.error("All fields are required")
            return
        if password != confirm_password:
            st.error("Passwords do not match")
        else:
            hashed_password = hash_password(password)
            users_collection.insert_one({
                "username": username,
                "email": email,
                "password": hashed_password,
                "alpaca_key": alpaca_key,
                "alpaca_secret_key": alpaca_secret_key
            })
            st.success("Account created successfully. You can now log in.")
            

# Initialize session state if not already initialized
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'email' not in st.session_state:
    st.session_state.email = ""
if 'alpaca_key' not in st.session_state:
    st.session_state.alpaca_key = None
if 'alpaca_secret_key' not in st.session_state:
    st.session_state.alpaca_secret_key = None
if 'predictions' not in st.session_state:
    st.session_state.predictions = None
if 'last_actual_value' not in st.session_state:
    st.session_state.last_actual_value = None
if 'plotly_fig' not in st.session_state:
    st.session_state.plotly_fig = None
if 'bot_status' not in st.session_state:
    st.session_state.bot_status = None
if 'is_thread_running' not in st.session_state:
    st.session_state.is_thread_running = False

def login():
    st.header("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Log In"):
        user = users_collection.find_one({"email": email})
        if user and verify_password(password, user["password"]):
            st.success(f"Logged in as {user['username']}")
            st.session_state.username = user['username']
            st.session_state.email = user['email']
            st.session_state.alpaca_key = user['alpaca_key']
            st.session_state.alpaca_secret_key = user['alpaca_secret_key']
        else:
            st.error("Invalid email or password")

def check():
    # Display the login/signup page or the dashboard page
    if st.session_state.username == "":
        # Display the login/signup page
        page = st.sidebar.selectbox("Select Page", ["Login", "Sign Up"])
        if page == "Login":
            login()
        elif page == "Sign Up":
            signup()

    else:

        # Display content after successful login
        st.sidebar.success(f"Logged in as {st.session_state.username}")
        selected_page = st.sidebar.selectbox("**Select a Page**", ["Live Stock", "Quick Trade", "Portfolio", "Trading Bot","Bot Info","Profile"])
        key = st.session_state.alpaca_key
        secret = st.session_state.alpaca_secret_key
        st.session_state.predict = []

        # Add a line in the sidebar
        st.sidebar.markdown('-------------------------')

       

check()