import streamlit as st
import requests
from streamlit_extras.switch_page_button import switch_page

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

def main():
    st.title("Login Page")

    # Input fields for email and password
    username = st.text_input("Username:")
    password = st.text_input("Password:", type="password")

    if st.button("Login"):
        # Validate the login credentials
        user_id = authenticate_user(username, password)
        if user_id:
            st.markdown(f'<meta http-equiv="refresh" content="0;URL=http://localhost:8502/?id={user_id}">', unsafe_allow_html=True)
        else:
            st.error("Invalid email or password")

    st.markdown("Dont have an account yet?")
    if st.button("Sign Up"):
        switch_page("create")


def authenticate_user(username, password):
    login_url = "http://127.0.0.1:8000/user/login"
    
    # Your authentication payload (username and password)
    payload = {"username": username, "password": password}
    
    # Make a POST request to the login endpoint with JSON payload
    response = requests.post(login_url, json=payload)
    
    if response.status_code == 200:
        print("Login successful!")
        return response.json().get("_id")
    else:
        print(f"Login failed. Status code: {response.status_code}, Details: {response.text}")
        return False


if __name__ == "__main__":
    main()
 