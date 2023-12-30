from datetime import datetime
import pandas as pd
import os

# Alpaca
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame

class backtestClass:

    def __init__(_self):
        
        # Alpaca Trading Client
        _self.trading_client = TradingClient('PK6E2ZBVAC6AHFH4EA2H', 'qeuDzKQWTnY7uMdJ3sFXiQs34VjFup4teeaxelOn', paper=True)
        _self.client = CryptoHistoricalDataClient()
        _self.account = _self.trading_client.get_account()

    # Get historical price data
    def get_historical_data(_self, symbol, start_date, end_date):
        
        # Empty the file
        file_path = 'backtestingData\history_btc.csv'
        header = "timestamp,open,high,low,close,volume,trade_count,vwap\n"
        with open(file_path, 'w') as file:
            file.write(header)

        try:
            # Convert input start_date and end_date to datetime objects
            start_date = datetime.strptime(start_date, "%d-%m-%Y")
            end_date = datetime.strptime(end_date, "%d-%m-%Y")

            # Creating request object for historical data
            historical_request_params = CryptoBarsRequest(
                symbol_or_symbols=[symbol],
                timeframe=TimeFrame.Minute,
                start=start_date,
                end=end_date
            )

            # Retrieve historical data for the specified symbol in a DataFrame
            historical_btc_bars = _self.client.get_crypto_bars(historical_request_params)
            historical_df = historical_btc_bars.df
            historical_df = historical_df.drop(columns=historical_df.columns.difference(['open', 'high', 'low', 'close', 'volume']))
            historical_df = historical_df.reset_index()
            historical_df = historical_df.drop(columns=['symbol']).set_index('timestamp')

            # Append the new data to 'history_btc.csv' or create a new file
            history_filename = 'backtestingData/history_btc.csv'
            historical_df.to_csv(history_filename, mode='a', header=not os.path.exists(history_filename), index=True)
            print("Historical data saved successfully!")

        except Exception as e:
            print(f"Error fetching historical data: {e}")


    def backtest_history(_self):
        
        # Empty the file
        file_path = 'backtestingData\history_transaction.csv'
        header = "Robot Name,Time,Transaction ID,Type\n"
        with open(file_path, 'w') as file:
            file.write(header)

        try:
            
            # Read historical transactions data from 'history_transaction.csv'
            historical_data_file = 'backtestingData/history_btc.csv'
            historical_data = pd.read_csv(historical_data_file)

            # Use the first 30 rows as the initial previous_row
            previous_row = historical_data.iloc[:100].copy() if len(historical_data) >=500 else historical_data.copy()
            
            # Loop through each row (starting from the 31st row)
            for i in range(100, len(historical_data)):

                # Create a copy of the current row
                current_row = historical_data.iloc[i:i+1].copy()

                # Concatenate previous_row and current_row into all_row
                all_row = pd.concat([previous_row, current_row], ignore_index=True)

                # Convert 'timestamp' column to datetime and set it as the index
                all_row['timestamp'] = pd.to_datetime(all_row['timestamp'])
                all_row.set_index('timestamp', inplace=True)

                # Call the buy function with all_row
                _self.price_change_buy_history(all_row)

                # Update previous_row for the next iteration
                previous_row = all_row.copy()

        except Exception as e:
            print(f"Error processing historical transactions: {e}")
    
    # Fetch all robot data
    def fetch_all_robot(_self):
        try:
            # Read data from 'robots.csv'
            robots_data = pd.read_csv('Data/robots.csv')
            return robots_data

        except Exception as e:
            print(f"Error fetching robot data: {e}")
            return None
        
    def price_change_buy_history(_self, all_row):
        
        # Fetch all robot data outside the loop
        all_robot_data = _self.fetch_all_robot()
        
        
        for _, row in all_robot_data.iterrows():
            robot_name = row['Robot Name']
            status = row['Status']
            strategy = row['Stratergy']

            # Check if the status is "Running" before triggering the strategy
            if status == "Running":

                # Execute the corresponding strategy method
                if strategy == "MACD&RSI":
                    buy_signal, sell_signal = _self.macd_rsi_strategy(all_row)
                # elif strategy == "MA&BOL":
                #     buy_signal, sell_signal = _self.ma_bol_strategy(close_prices)

                # Execute buy and sell orders based on signals
                if buy_signal:
                    _self.buy_history(row['Symbol'], row['Quantity'], robot_name)
                    print(f"{robot_name} bought")
                elif sell_signal:
                    # Check available quantity before selling
                    position = _self.trading_client.get_open_position(row['Symbol'].replace("/", ""))
                    available_quantity = float(position.qty_available) if position else 0

                    # Compare available quantity with the quantity the bot wants to sell
                    if available_quantity >= row['Quantity']:
                        _self.sell_history(row['Symbol'], row['Quantity'], robot_name)
                        print(f"{robot_name} sold")
                    else:
                        print(f"Not enough {row['Symbol']} to sell.")
                else:
                    print("No buying or selling this round.")
            
            #Robot is not running
            else:
                print(robot_name + "is not running")
                continue
                    
    
    # preparing BUY market orders
    def buy_history(_self, symb, quantity, robot_name):
        try:
            # For ID, use time
            formatted_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

            market_order_data = MarketOrderRequest(
                symbol=symb,
                qty=quantity,
                side=OrderSide.BUY,
                time_in_force=TimeInForce.IOC,
                client_order_id= formatted_time,
            )  

            # Market order
            market_order = _self.trading_client.submit_order(order_data=market_order_data)

            # Get the order's Client Order ID
            order_id = _self.trading_client.get_order_by_client_id(market_order_data.client_order_id)

            # Append order information to transactions.csv
            order_info = {'robot_name': robot_name, 'client_order_id': market_order_data.client_order_id, 'order_id': order_id.id, 'type': "Buy"} #, 'filled_price': filled_avg_price
            transactions_data = pd.DataFrame([order_info])
            transactions_data.to_csv('backtestingData\history_transaction.csv', mode='a', header=not os.path.exists('backtestingData\history_transaction.csv'), index=False)

        except Exception as e:
            print(f"Error placing buy order: {e}")

    # preparing SELL market orders
    def sell_history(_self, symb, quantity, robot_name):
        try:
            # For ID, use time
            formatted_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

            market_order_data = MarketOrderRequest(
                symbol=symb,
                qty=quantity,
                side=OrderSide.SELL,
                time_in_force=TimeInForce.IOC,
                client_order_id= formatted_time,
            )  

            # Market order
            market_order = _self.trading_client.submit_order(order_data=market_order_data)

            # Get the order's Client Order ID
            order_id = _self.trading_client.get_order_by_client_id(market_order_data.client_order_id)

            # Append order information to transactions.csv
            order_info = {'robot_name': robot_name, 'client_order_id': market_order_data.client_order_id, 'order_id': order_id.id, 'type': "sell"} #, 'filled_price': filled_avg_price
            transactions_data = pd.DataFrame([order_info])
            transactions_data.to_csv('backtestingData\history_transaction.csv', mode='a', header=not os.path.exists('backtestingData\history_transaction.csv'), index=False)

        except Exception as e:
            print(f"Error placing sell order: {e}")
    
