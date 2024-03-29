import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from alpacas import alpacaClass
from robot import robotClass
import time
from datetime import datetime
from PIL import Image
from streamlit_extras.app_logo import add_logo

st.set_page_config(layout="wide", initial_sidebar_state="collapsed",page_title="Home", page_icon = ":money_with_wings:")

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

############################################# Alpaca Dashboard ##########################################

# Create alpaca user
alpaca_user = alpacaClass(username_param)
robot_user = robotClass(username_param)

welcome_string = f"Welcome back {alpaca_user.username}!"
st.title(welcome_string)
st.markdown("")

# creating a single-element container
placeholder = st.empty()


# Loop to fetch current minute's data every 10 seconds
while True:

    # Update real-time data
    alpaca_user.continuousMethods()
    robot_user.updateProfit()

    with sidebarContainer.container():
    
        logs = pd.read_csv("logs.csv")
        logs = logs.tail(5)
        st.markdown("")
        st.dataframe(logs, hide_index=True, use_container_width = True)

    with placeholder.container():

    
        ################################################ First container of real time close prices with 5 column

        # Images of each crypto
        alpaca_image = Image.open("pics/alpaca.png")
        btc_image = Image.open("pics/btc.png")
        eth_image = Image.open("pics/eth.png")
        link_image = Image.open("pics/link.png")
        ltc_image = Image.open("pics/ltc.png")
        more_image = Image.open("pics/more.png")
        info_image = Image.open("pics/info.png")

        # Fetch real time close prices
        closePrices = alpaca_user.getRealTimePrices()
        
        def get_close_values(close_prices, symbol):
            try:
                current_close = round(close_prices.loc[close_prices['symbol'] == symbol, 'current_close'].values[0], 2)
                last_close = round(close_prices.loc[close_prices['symbol'] == symbol, 'last_close'].values[0], 2)
                return current_close, last_close
            except IndexError:
                # If index is out of bounds, return 0.0 for both values
                return 0.0, 0.0
    
        # BTC KPI
        btc_current_close, btc_last_close = get_close_values(closePrices, 'btc')
        btc_close = "${:,.2f}".format(btc_current_close)
        delta_btc = round(btc_current_close - btc_last_close, 2)

        # ETH KPI
        eth_current_close, eth_last_close = get_close_values(closePrices, 'eth')
        eth_close = "${:,.2f}".format(eth_current_close)
        delta_eth = round(eth_current_close - eth_last_close, 2)

        # LTC KPI
        ltc_current_close, ltc_last_close = get_close_values(closePrices, 'ltc')
        ltc_close = "${:,.2f}".format(ltc_current_close)
        delta_ltc = round(ltc_current_close - ltc_last_close, 2)

        # LINK KPI
        link_current_close, link_last_close = get_close_values(closePrices, 'link')
        link_close = "${:,.2f}".format(link_current_close)
        delta_link = round(link_current_close - link_last_close, 2)
        
        statusColumn, btcColumn, ethColumn, ltcColumn, linkColumn = st.columns([0.98,1,0.9,0.8,0.8])

        with statusColumn:
             
            statusContainer = st.container(border=True)

            with statusContainer:

                status1, status2 = st.columns([0.4, 1])

                with status1:
                    st.markdown("")
                    st.image(alpaca_image, width=50, use_column_width=False)
                    st.markdown("")

                with status2:

                    options = ["Paper Trading"]
                    selected_option = st.selectbox("Trading mode:", options, index=options.index("Paper Trading"), key = datetime.utcnow() ,help="Paper trading simulates trades without involving real money.")
                    st.subheader("")

                
        with btcColumn:
             
            btcContainer = st.container(border=True)

            with btcContainer:

                btc1, btc2 = st.columns([0.4, 1])

                with btc1:
                    st.markdown("")
                    st.image(btc_image, width=50, use_column_width=False)
                    st.markdown("")

                btc2.metric(

                        label="Bitcoin",
                        value=btc_close,
                        delta=delta_btc
                        
                    )
                
        with ethColumn:
             
            ethContainer = st.container(border=True)

            with ethContainer:

                eth1, eth2 = st.columns([0.4, 1])

                with eth1:
                    st.markdown("")
                    st.image(eth_image, width=50, use_column_width=False)
                    st.markdown("")

                eth2.metric(
                        label="Ethereum",
                        value=eth_close,
                        delta=delta_eth
                    )  
                   
                
        with ltcColumn:
             
            ltcContainer = st.container(border=True)

            with ltcContainer:

                ltc1, ltc2 = st.columns([0.4, 1])

                with ltc1:
                    st.markdown("")
                    st.image(ltc_image, width=50, use_column_width=False)
                    st.markdown("")

                ltc2.metric(
                        label="Litecoin",
                        value=ltc_close,
                        delta=delta_ltc
                    )
            
                
        with linkColumn:
             
            linkContainer = st.container(border=True)

            with linkContainer:

                link1, link2 = st.columns([0.4, 1])

                with link1:
                    st.markdown("")
                    st.image(link_image, width=50, use_column_width=False)
                    st.markdown("")

                link2.metric(
                        label="Chainlink",
                        value=link_close,
                        delta=delta_link
                    ) 
        
        ################################################ Second container with 2 column (assets)

        donutColumn, assetColumn   = st.columns([1.1,4])

        # Read the account info from the CSV file
        accountInfo = pd.read_csv('Data/accountInfo.csv', parse_dates=['timestamp'])
        accountInfo = accountInfo.tail(100)
        
        # Define a function to handle missing values
        def get_previous_value(column):
            return column.iloc[-2] if len(column) >= 2 else 0.0
        
        def get_column(column):
            return column.iloc[-1] if not column.empty else 0.0

        # Extracting the last two rows for each column of interest
        buying_power_last = get_previous_value(accountInfo['buying power'])
        buying_power_current = get_column(accountInfo['buying power'])
        buying_power_delta = float(buying_power_current - buying_power_last)
        buying_power_data = '${:,.2f}'.format(buying_power_current)

        equity_last = get_previous_value(accountInfo['equity'])
        equity_current = get_column(accountInfo['equity'])
        equity_delta = float(equity_current - equity_last)
        equity_data = '${:,.2f}'.format(equity_current)

        cash_last = get_previous_value(accountInfo['cash'])
        cash_current = get_column(accountInfo['cash'])
        cash_delta = float(cash_current - cash_last)
        cash_data = '${:,.2f}'.format(cash_current)

        pnl_last = get_previous_value(accountInfo['pnl'])
        pnl_current = get_column(accountInfo['pnl'])
        pnl_delta = round(pnl_current - pnl_last,2)
        pnl_data = '${:,.2f}'.format(pnl_current)

        with assetColumn:

            cashContainer = st.container(border=True)

            with cashContainer:
                    
                    bp, eq, csh, pl = st.columns(4)

                    # Buying power
                    bp.metric(
                        label="Buying Power",
                        value= buying_power_data,
                        delta= buying_power_delta,
                        help="Buying Power represents the available funds for new trades."
                    )

                    # Equity
                    eq.metric(
                        label="Equity",
                        value= equity_data, 
                        delta=equity_delta,
                        help="Equity is the total value of your investments."
                    )

                    #Cash
                    csh.metric(
                        label="Cash",
                        value= cash_data, 
                        delta=cash_delta,
                        help="Cash denotes the available liquid funds."
                    )

                    # Daily PnL
                    pl.metric(
                        label="Daily PnL",
                        value= pnl_data,
                        delta=pnl_delta,
                        help="Daily P&L reflects the profit or loss incurred on the current trading day."
                    )

        ################################################ Third container with 2 line graphs (assets)

            assetContainer = st.container(border=True)

            with assetContainer:

                equityColumn, pnlColumn = st.columns(2)

                with equityColumn:

                    # Create a line chart for equity
                    fig_equity = go.Figure()
                    fig_equity.add_trace(go.Scatter(x=accountInfo['timestamp'], y=accountInfo['equity'], mode='lines', name='Equity'))
                    fig_equity.update_layout(title='Equity Over Time', xaxis_title='Timestamp', yaxis_title='Equity', height=340, width=450)
                    fig_equity.update_layout(margin=dict(l=100, r=0, t=50, b=0))

                    st.plotly_chart(fig_equity)

                with pnlColumn:

                    # Create a line chart for PnL
                    fig_pnl = go.Figure()
                    fig_pnl.add_trace(go.Scatter(x=accountInfo['timestamp'], y=accountInfo['pnl'], mode='lines', name='PnL'))
                    fig_pnl.update_layout(title='PnL Over Time', xaxis_title='Timestamp', yaxis_title='PnL', height=340, width=450)
                    fig_pnl.update_layout(margin=dict(l=50, r=0, t=50, b=0))

                    st.plotly_chart(fig_pnl)

        with donutColumn:
             
            donutContainer = st.container(border=True)

            with donutContainer:

                try:
                    asset_data = pd.read_csv('Data/asset.csv')
                except pd.errors.EmptyDataError:
                    # Create an empty DataFrame with headers
                    columns = ['Symbol', 'Quantity', 'Price', 'Market Value', 'Total P&L']
                    asset_data = pd.DataFrame(columns=columns)

                # Convert the 'cash' value to float
                cash_value = float(cash_data.replace('$', '').replace(',', ''))

                # Initialize lists with 'Cash' label and value
                labels = ['Cash']
                values = [cash_value]

                # Iterate through rows in asset_data and append to labels and values
                for index, row in asset_data.iterrows():
                    labels.append(row['Symbol'])
                    
                    # Remove the '$' sign and convert to float
                    market_value = float(row['Market Value'].replace('$', '').replace(',', ''))
                    values.append(market_value)


                # Create a donut chart
                fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.3)])

                # Update layout for better visualization
                fig.update_layout(
                    showlegend=False,
                    height=180,  # set the height in pixels
                    width=270,    # set the width in pixels
                    paper_bgcolor='rgba(0,0,0,0)',  # set the background color to transparent
                    plot_bgcolor='rgba(0,0,0,0)',  # set the plot area color to transparent
                    margin=dict(l=0, r=0, t=70, b=5) # set margins to zero
                )

                t1 ,  mid, t2 , = st.columns([0.45,1,0.2])

                with mid:
                    st.markdown("Your Portfolio", help="The portfolio diagram illustrates your cash position and asset distribution.")
                
                # Update config to hide the fullscreen button
                st.plotly_chart(fig, config={'displayModeBar': False})

                st.markdown("")
                st.markdown("")
                # Show asset and throw exception
                try:
                    # Read live data from 'asset.csv' file
                    asset_table = pd.read_csv('Data/asset.csv')
                    asset_table = asset_table.set_index('Symbol')

                    # Extract the desired columns
                    selected_data = asset_table.drop(columns=asset_table.columns.difference(['Symbol', 'Quantity', 'Market Value']))
                    st.table(selected_data)

                
                except Exception as e:
                    # Handle the error, and create an empty DataFrame
                    empty_data = pd.DataFrame(columns=['Symbol', 'Quantity', 'Market Value'])
                    st.table(empty_data, hide_index=True)
                
                st.markdown("")
                st.markdown("")
                st.subheader("")
            
        with st.expander("Latest transactions"):
            
            # Read data from 'Data/transactions.csv' into a DataFrame
            transactions_data = alpaca_user.get_transactions()
            transactions_data = transactions_data.drop(columns=['Username'])

            # Display the last 5 rows of the DataFrame
            last_5_transactions = transactions_data.tail(10)
            st.dataframe(last_5_transactions, hide_index=True, use_container_width = True)

        # Wait for 10 seconds before the next iteration
        time.sleep(11)

