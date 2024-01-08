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


def main():
    st.title("Welcome to Quantum Trading")
    st.subheader("Empowering your trading experience with quantum technology")

    # Add any other content or information about your app

    # Button to navigate to the login page
    sign, log = st.columns(2)

    with sign:
        if st.button("Sign Up"):
            switch_page("create")
    
    with log:
        if st.button("Log in"):
            switch_page("login")


if __name__ == "__main__":
    main()
