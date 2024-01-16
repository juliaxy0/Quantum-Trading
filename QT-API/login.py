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

def main():


    cc, mid, ccc = st.columns([0.3,1,0.3])

    with mid:

        st.markdown("<h2 style='text-align:center'>Quantum Trading</h2>", unsafe_allow_html=True)

        st.write("Where youre investing experience are elevated.")

        with st.form("create_user_form"):

            # Input fields for email and password
            email = st.text_input("Email:")
            password = st.text_input("Password:", type="password")
            st.markdown("")

            c1 ,  button, c2 , = st.columns([1,1,1])

            with button:

                if st.form_submit_button("Login", type="primary",use_container_width=True):
                    # Validate the login credentials
                    user_id = authenticate_user(email, password)
                    if user_id:
                        st.markdown(f'<meta http-equiv="refresh" content="0;URL=http://localhost:8501/landing/?id={user_id}">', unsafe_allow_html=True)
                    else:
                        st.error("Invalid email or password")

        st.markdown("")

        if st.button("Dont have an account yet?  Sign Up"):
            switch_page("create")
   
    
def authenticate_user(email, password):
    login_url = "http://127.0.0.1:8000/user/login"
    
    # Your authentication payload (username and password)
    payload = {"email": email, "password": password}
    
    # Make a POST request to the login endpoint with JSON payload
    response = requests.post(login_url, json=payload, timeout=30)
    
    if response.status_code == 200:
        print("Login successful!")
        data = response.json()
        return data.get("_id")
    else:
        print(f"Login failed. Status code: {response.status_code}, Details: {response.text}")
        return False


if __name__ == "__main__":
    main()
 