from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import pandas as pd
import time

# Alpaca
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetAssetsRequest
from alpaca.trading.enums import AssetClass
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.requests import LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame

class robotClass:

    def __init__(_self):
        
        # Alpaca Trading Client
        _self.trading_client = TradingClient('PKB0LG2EODH45BRZMGOJ', 'dRlvGD5F3Kovjfv8ZZ2OoxjT5hLSWRLL1pcmgqv7', paper=True)
        _self.order_df = pd.DataFrame(columns=['robot_name', 'client_order_id', 'order_id'])

        # Robot 
        
        # _self.robot_run()      

    def create_robot(_self, symbol, quantity, robot_name):

        _self.robot_array = pd.DataFrame(columns=['symbol', 'quantity', 'robot_name', 'status'])

        # Create a DataFrame with the information of the newly created robot
        robot_info = pd.DataFrame({'symbol': [symbol], 'quantity': [quantity], 'robot_name': [robot_name], 'status': [False]})
        
        # Concatenate the new DataFrame with the existing robot_array
        _self.robot_array = pd.concat([_self.robot_array, robot_info], ignore_index=True)

    # Updatatus of robot
    def update_status(_self, robot_name, new_status):
        _self.robot_array.loc[_self.robot_array['robot_name'] == robot_name, 'status'] = new_status

    # Return the robot array 
    def get_robot_array(_self):
        return _self.robot_array
    
    # preparing market orders
    def buy(_self, symb, quantity, robot_name):

        market_order_data = MarketOrderRequest(
            symbol=symb,
            qty=quantity,
            side=OrderSide.BUY,
            time_in_force=TimeInForce.IOC,
            client_order_id=f'ordedfrrdrcs{len(_self.order_df) + 1}',
        )

        # Market order
        market_order = _self.trading_client.submit_order(order_data=market_order_data)

        # Get the order's Client Order ID
        order_id = _self.trading_client.get_order_by_client_id(market_order_data.client_order_id)

        # Append order information to the DataFrame
        order_info = {'robot_name': robot_name, 'client_order_id': market_order_data.client_order_id, 'order_id': order_id.id}
        _self.order_df = pd.concat([_self.order_df, pd.DataFrame([order_info])], ignore_index=True)


    # # run robot
    # def robot_run(_self):
    #     while True:
    #         for index, row in _self.robot_array.iterrows():
    #             if row['status']:
    #                 _self.buy(row['symbol'], row['quantity'], row['robot_name'])
            

