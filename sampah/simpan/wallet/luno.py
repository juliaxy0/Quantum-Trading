
from luno_python.client import Client
import streamlit as st

# username = 'gs9grmdr5czk'
# password ='meVXjM4M2xekUpuawNIzGBDu1QEH75hQjGMec8QhUsc'

# if __name__ == '__main__':
#     connection = Client(api_key_id=username, api_key_secret=password)
#     get_assets(connection)
    # get_candles(connection)
    
class Luno:
    def __init__(_self,username,password):
        _self.connection = Client(api_key_id=username, api_key_secret=password)
        _self.luno_wallet = [
        {'asset': 'BTC', 'balance': 0.0},
        {'asset': 'ETH', 'balance': 0.0},
        {'asset': 'BNB', 'balance': 0.0},
        {'asset': 'LTC', 'balance': 0.0},
        {'asset': 'MYR', 'balance': 0.0},
        {'asset': 'XRP', 'balance': 0.0},
        ]

    @st.cache_data(show_spinner=False)
    def get_assets(_self):
        assets = Client.get_balances(_self.connection)
        assets = assets['balance']

        # inserting every crypto in wallet
        _self.luno_wallet =[]
        for data in assets:
            asset = data['asset']
            balance = data['balance']
            _self.luno_wallet.append((asset, balance))    
        return _self.luno_wallet

    def get_candles(self):
        data = self.get_candles(300, 'XBTMYR', 1635500000000)

        # Print the close prices
        for candle in data:
            timestamp = candle['timestamp']
            close_price = candle['close']['price']
            print(f"Timestamp: {timestamp}, Close Price: {close_price}")


