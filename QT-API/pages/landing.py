import streamlit as st

st.set_page_config(initial_sidebar_state="collapsed")

user_id = st.experimental_get_query_params().get("id", [""])[0]

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
    st.title("")
    

    # Add any other content or information about your app

    # Button to navigate to the login page
    crypto, stock = st.columns(2)

    with crypto:
        if st.button("Cryptocurrency"):
            st.markdown(f'<meta http-equiv="refresh" content="0;URL=http://localhost:8502/?id={user_id}">', unsafe_allow_html=True)
    
    with stock:
        if st.button("Stock"):
            st.markdown(f'<meta http-equiv="refresh" content="0;URL=http://localhost:8502/?id={user_id}">', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
