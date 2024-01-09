import streamlit as st
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

st.subheader("Create an account")

# Use st.form to create the form
with st.form("create_user_form"):

    
    # Input fields in the form
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    api_key = st.text_input("API Key")
    secret_key = st.text_input("Secret Key", type="password")

    # Submit button inside the form
    submitted = st.form_submit_button("Create User")

# Check if the form is submitted
if submitted:
    st.success("User created successfully!")


st.markdown("Already have an account?")
if st.button("Login"):
        switch_page("login")
