import streamlit as st
import streamlit.components.v1 as components

user_id = st.experimental_get_query_params().get("id", [""])[0]

st.set_page_config(initial_sidebar_state="collapsed",layout="wide")

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
    _,col1,_ = st.columns([0.25,0.3,0.25])
    col1.image("pics/land.png")  
    
    st.title("")
    

    # Add any other content or information about your app

    # Button to navigate to the login page
    crypto, stock = st.columns(2)

    with crypto:
        with st.container(border=True):

            st.markdown("")
            st.markdown("")
            
            cmore, cim,cdesc,cehe  = st.columns([0.1,1,1,0.2])
            with cim:
                st.markdown("")
                st.markdown("")
            cim.image("pics/crypto.png", width = 250)

            with cdesc:
                st.subheader("Crypto Currency")
                st.markdown("Dive into the dynamic realm of crypto trading, where the markets pulse with volatility and each trade unlocks the potential for financial growth and strategic maneuvers across diverse digital assets like Bitcoin and Ethereum")
            
            st.markdown("")

            _,cbut,_ = st.columns([0.4,0.6,0.4])

            if cbut.button("# Go Now!", use_container_width=True,key="crypto"):
                st.markdown(f'<meta http-equiv="refresh" content="0;URL=http://localhost:8502/?id={user_id}">', unsafe_allow_html=True)
            # ChangeButtonColour("Go Now!", "#FDFD96")
            st.markdown("")
            st.markdown("")
            
    with stock:
        with st.container(border=True):

            st.markdown("")
            st.markdown("")
            
            im,desc,more = st.columns([1,1,0.1])
            with im:
                st.markdown("")
                st.markdown("")
            im.image("pics/stock.png", width = 250)

            with desc:
                st.subheader("Stock Market")
                st.markdown("")
                st.markdown("Discover the heart of financial dynamism at the stock market. Seamlessly buy and sell shares, capitalizing on company performance and economic indicators to unlock unparalleled avenues of growth.")
            desc.markdown("")

            st.subheader("")

            _,sbut,_ = st.columns([0.4,0.6,0.4])

            st.markdown(
                """
                <style>
                button[kind="secondary"] {
                    background: #e8d035!important;
                    padding: 10px 32px !important;
                    height: auto;
                    padding-top: 2px !important;
                    padding-bottom: 2px !important;
                    font-weight: bold !important;
                    cursor: pointer !important;
                    font-size: 15px !important;
                    color: black !important;
                }
                button[kind="secondary"]:hover {
                    text-decoration: none;
                    color: white !important;
                }
                button[kind="secondary"]:focus {
                    outline: none !important;
                    color: white !important;
                }
                </style>
                """,
                unsafe_allow_html=True,
            )

            if sbut.button("# Go Now!", use_container_width=True,key="stock",type="secondary"):
                st.markdown(f'<meta http-equiv="refresh" content="0;URL=http://localhost:8502/?id={user_id}">', unsafe_allow_html=True)
            
            

if __name__ == "__main__":
    main()
