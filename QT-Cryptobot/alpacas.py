from datetime import datetime, timedelta, timezone
import pandas as pd
import os
import csv

# Config 
from config import *

# Alpaca
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame

# Import classes
from stratergies import stratergiesClass

from robot import robotClass

# TODO : get files method, dont let view read directly

class alpacaClass:

    def __init__(_self):
        
        # Alpaca Trading Client
        _self.trading_client = TradingClient(API_KEY, SECRET_KEY, paper=True)
        _self.client = CryptoHistoricalDataClient()
        _self.account = _self.trading_client.get_account()
        
        # Real time data files
        _self.initializeFiles()

        # Fetch initial real time data
        _self.get_initial_btc_data()
        _self.get_initial_eth_data()
        _self.get_initial_ltc_data()
        _self.getAccountDetails()

    #################################### home.py
  
    def continuousMethods(_self):
        _self.fetch_real_time_btc_data()
        _self.fetch_real_time_eth_data()
        _self.fetch_real_time_ltc_data()
        _self.fetch_real_time_link_data()
        _self.getAccountDetails()
        _self.get_asset()
        _self.cleanFiles()

    def getAccountDetails(_self):
        try:
            # Get the current timestamp with hour, minute, and seconds
            current_time = datetime.utcnow().replace(tzinfo=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

            # Buying power 
            bp = float(_self.account.buying_power)

            # Equity
            equity = _self.account.equity

            # Cash
            cash = float(_self.account.cash)

            # PnL
            pnl = float(_self.account.equity) - float(_self.account.last_equity)

            # Create a new row DataFrame
            new_row = pd.DataFrame({'timestamp': [current_time], 'buying power': [bp], 'equity': [equity], 'cash': [cash], 'pnl': [pnl]})

            # Load existing DataFrame from CSV file or create an empty DataFrame with the header
            try:
                existing_data = pd.read_csv('Data/accountInfo.csv', parse_dates=['timestamp'])
            except FileNotFoundError:
                header = ['timestamp', 'buying power', 'equity', 'cash', 'pnl']
                existing_data = pd.DataFrame(columns=header)

            # Concatenate existing data with the new row
            updated_data = pd.concat([existing_data, new_row], ignore_index=True)

            # Save the updated DataFrame to CSV file
            updated_data.to_csv('Data/accountInfo.csv', index=False)

        except Exception as e:
            print(f"Error fetching account details: {e}")

    def get_asset(_self):
        try:
            # Get a list of all of our positions.
            portfolio = _self.trading_client.get_all_positions()

            with open('Data/asset.csv', 'w', newline='') as csv_file:
                csv_writer = csv.writer(csv_file)

                # Write header
                csv_writer.writerow(['Symbol', 'Quantity', 'Price', 'Market Value', 'Total P&L'])

                # Write each row to the CSV file
                for position in portfolio:

                    symbol = position.symbol
                    quantity = position.qty
                    price1 = float(position.current_price)
                    market_val1 = float(position.market_value)
                    pnl1 = float(position.unrealized_pl)

                    # Format 
                    price = "${:,.2f}".format(price1)
                    market_val = "${:,.2f}".format(market_val1)
                    pnl = "${:,.2f}".format(pnl1)

                    csv_writer.writerow([symbol, quantity, price, market_val, pnl ])

        except Exception as e:
            return f"Error getting portfolio: {e}"
    
    #################################### real-time dashboard.py

    ####################### Displaying real time crypto data

    def getRealTimePrices(_self):
        # Directory where the CSV files are stored
        data_directory = 'Data'

        # List of crypto symbols
        crypto_symbols = ['btc', 'eth', 'ltc', 'link']

        # Initialize an empty list to store DataFrames
        dfs = []

        # Iterate through each crypto symbol
        for symbol in crypto_symbols:
            # Construct the file path
            file_path = os.path.join(data_directory, f'{symbol}.csv')

            # Check if the file exists
            if os.path.exists(file_path):
                # Read the CSV file into a DataFrame
                df = pd.read_csv(file_path)

                # Check if there are at least two rows
                if len(df) >= 2:
                    # Extract the relevant columns for the last two rows
                    last_row = df.iloc[-1]
                    second_last_row = df.iloc[-2]

                    # Create a new DataFrame with the extracted data
                    symbol_df = pd.DataFrame({
                        'symbol': [symbol],
                        'current_close': [last_row['close']],
                        'last_close': [second_last_row['close']]
                    })  

                    # Append the new DataFrame to the list
                    dfs.append(symbol_df)

        # Concatenate all DataFrames into a single DataFrame
        crypto_df = pd.concat(dfs, ignore_index=True)

        return crypto_df


    ####################### Real time crypto data


    def initializeFiles(_self):

        # Empty the btc file
        file_path = 'Data/btc.csv'
        header = "timestamp,open,high,low,close,volume,trade_count,vwap\n"
        with open(file_path, 'w') as file:
            file.write(header)

        # Empty the eth file
        file_path = 'Data/eth.csv'
        header = "timestamp,open,high,low,close,volume,trade_count,vwap\n"
        with open(file_path, 'w') as file:
            file.write(header)

        # Empty the ltc file
        file_path = 'Data/ltc.csv'
        header = "timestamp,open,high,low,close,volume,trade_count,vwap\n"
        with open(file_path, 'w') as file:
            file.write(header)

        # Empty the link file
        file_path = 'Data/link.csv'
        header = "timestamp,open,high,low,close,volume,trade_count,vwap\n"
        with open(file_path, 'w') as file:
            file.write(header)

        # Empty the account info file
        file_path = 'Data/accountInfo.csv'
        header = "timestamp,buying power,equity,cash,pnl\n"
        with open(file_path, 'w') as file:
            file.write(header)

        # Empty the asset file
        file_path = 'Data/asset.csv'
        header = "Symbol,Quantity,Price,Market Value,Total P&L\n"
        with open(file_path, 'w') as file:
            file.write(header)

        # Empty the profit file
        file_path = 'Data\profit.csv'
        header = "Robot Name,Profit,Timestamp\n"
        with open(file_path, 'w') as file:
            file.write(header)

    def cleanFiles(_self):

        files_to_clean = ['Data/accountInfo.csv', 'Data/asset.csv', 'Data/profit.csv']

        for file_path in files_to_clean:
            try:
                # Read the CSV file
                df = pd.read_csv(file_path)

                # Check if the row length is more than 100
                if len(df) > 100:
                    # Truncate the DataFrame to keep only the latest 100 rows
                    df = df.iloc[-80:]

                    # Save the truncated DataFrame back to the CSV file
                    df.to_csv(file_path, index=False)

            except Exception as e:
                print(f"Error cleaning {file_path}: {e}")

    
            
    ####################### BTC

    # Get initial price data
    def get_initial_btc_data(_self):

        # Calculate the start and end times for the initial data (e.g., 30 minutes ago)
        initial_start_time = datetime.utcnow() - timedelta(minutes=10)
        initial_end_time = datetime.utcnow()

        # Creating request object for initial data
        initial_request_params = CryptoBarsRequest(
            symbol_or_symbols=["BTC/USD"],
            timeframe=TimeFrame.Minute,
            start=initial_start_time,
            end=initial_end_time
        )

        # Retrieve initial data for Bitcoin in a DataFrame
        initial_btc_bars = _self.client.get_crypto_bars(initial_request_params)
        initial_df = initial_btc_bars.df
        initial_df = initial_df.reset_index()
        initial_df = initial_df.drop(columns=['symbol']).set_index('timestamp')

        # Append the new data to 'btc.csv' or create a new file
        initial_df.to_csv('Data/btc.csv', mode='a', header=not os.path.exists('Data/btc.csv'), index=True)
        
    # Update initial data to be real-time
    def fetch_real_time_btc_data(_self):
        try:
            # Set up the end time to the current time
            end_time = datetime.utcnow()

            # Calculate the start time as 10 minute ago
            start_time = end_time - timedelta(minutes=30)

            # Creating request object for current minute's data
            current_request_params = CryptoBarsRequest(
                symbol_or_symbols=["BTC/USD"],
                timeframe=TimeFrame.Minute,
                start=start_time,
                end=end_time
            )

            # Retrieve current minute's data for Bitcoin in a DataFrame
            current_btc_bars = _self.client.get_crypto_bars(current_request_params)
            current_df = current_btc_bars.df
            current_df = current_df.reset_index()
            current_df = current_df.drop(columns=['symbol']).set_index('timestamp')

            # Read existing data from the CSV file
            filename = 'Data/btc.csv'
            if os.path.isfile(filename):
                existing_data = pd.read_csv(filename, index_col='timestamp')
            else:
                existing_data = pd.DataFrame()

            # Filter out rows with timestamps that already exist in the CSV
            new_rows = current_df[~current_df.index.isin(existing_data.index)]

            # Append new data to 'btc.csv' only if there are new rows
            if not new_rows.empty:
                # Append value to the file
                new_rows.to_csv(filename, mode='a', header=not os.path.exists(filename))

                # Get the current updated data
                current_data = pd.read_csv(filename, index_col='timestamp')
                
                # Call robot
                _self.price_change_buy("BTC/USD", current_data)
                
        except Exception as e:
            print(f"Error updating BTC data: {e}")
            # Handle the exception as needed


    # Live data from CSV
    def get_live_btc_data(_self):
        try:
            # Read live data from 'btc.csv' file
            live_data = pd.read_csv('Data/btc.csv', parse_dates=['timestamp'])
            live_data = live_data.set_index('timestamp')

            return live_data
        except FileNotFoundError:
            print("Error: 'btc.csv' file not found. Please ensure the file exists.")
            return pd.DataFrame()  # Return an empty DataFrame if the file is not found
        except Exception as e:
            print(f"Error reading btc live data: {e}")
            return pd.DataFrame()  # Return an empty DataFrame for any other exception
        
    ####################### ETH

    # Get initial price data
    def get_initial_eth_data(_self):

        # Calculate the start and end times for the initial data (e.g., 30 minutes ago)
        initial_start_time = datetime.utcnow() - timedelta(minutes=30)
        initial_end_time = datetime.utcnow()

        # Creating request object for initial data
        initial_request_params = CryptoBarsRequest(
            symbol_or_symbols=["ETH/USD"],
            timeframe=TimeFrame.Minute,
            start=initial_start_time,
            end=initial_end_time
        )

        # Retrieve initial data for Bitcoin in a DataFrame
        initial_btc_bars = _self.client.get_crypto_bars(initial_request_params)
        initial_df = initial_btc_bars.df
        initial_df = initial_df.reset_index()
        initial_df = initial_df.drop(columns=['symbol']).set_index('timestamp')

        # Append the new data to 'eth.csv' or create a new file
        initial_df.to_csv('Data/eth.csv', mode='a', header=not os.path.exists('Data/eth.csv'), index=True)
        
    # Update initial data to be real-time
    def fetch_real_time_eth_data(_self):
        try:
            # Set up the end time to the current time
            end_time = datetime.utcnow()

            # Calculate the start time as 1 minute ago
            start_time = end_time - timedelta(minutes=10)

            # Creating request object for current minute's data
            current_request_params = CryptoBarsRequest(
                symbol_or_symbols=["ETH/USD"],
                timeframe=TimeFrame.Minute,
                start=start_time,
                end=end_time
            )

            # Retrieve current minute's data for Bitcoin in a DataFrame
            current_btc_bars = _self.client.get_crypto_bars(current_request_params)
            current_df = current_btc_bars.df
            current_df = current_df.reset_index()
            current_df = current_df.drop(columns=['symbol']).set_index('timestamp')

            # Read existing data from the CSV file
            filename = 'Data/eth.csv'
            if os.path.isfile(filename):
                existing_data = pd.read_csv(filename, index_col='timestamp')
            else:
                existing_data = pd.DataFrame()

            # Filter out rows with timestamps that already exist in the CSV
            new_rows = current_df[~current_df.index.isin(existing_data.index)]

            # Append new data to 'eth.csv' only if there are new rows
            if not new_rows.empty:
                # Append value to the file
                new_rows.to_csv(filename, mode='a', header=not os.path.exists(filename))

                # Get the current updated data
                current_data = pd.read_csv(filename, index_col='timestamp')
                
                # Call robot
                _self.price_change_buy("ETH/USD",current_data)
                

        except Exception as e:
            print(f"Error updating ETH data: {e}")
            # Handle the exception as needed


    # Live data from CSV
    def get_live_eth_data(_self):
        try:
            # Read live data from 'btc.csv' file
            live_data = pd.read_csv('Data/eth.csv', parse_dates=['timestamp'])
            live_data = live_data.set_index('timestamp')

            return live_data
        except FileNotFoundError:
            print("Error: 'eth.csv' file not found. Please ensure the file exists.")
            return pd.DataFrame()  # Return an empty DataFrame if the file is not found
        except Exception as e:
            print(f"Error reading eth live data: {e}")
            return pd.DataFrame()  # Return an empty DataFrame for any other exception
        
    ####################### LTC

    # Get initial price data
    def get_initial_ltc_data(_self):

        # Calculate the start and end times for the initial data (e.g., 30 minutes ago)
        initial_start_time = datetime.utcnow() - timedelta(minutes=30)
        initial_end_time = datetime.utcnow()

        # Creating request object for initial data
        initial_request_params = CryptoBarsRequest(
            symbol_or_symbols=["LTC/USD"],
            timeframe=TimeFrame.Minute,
            start=initial_start_time,
            end=initial_end_time
        )

        # Retrieve initial data for Bitcoin in a DataFrame
        initial_btc_bars = _self.client.get_crypto_bars(initial_request_params)
        initial_df = initial_btc_bars.df
        initial_df = initial_df.reset_index()
        initial_df = initial_df.drop(columns=['symbol']).set_index('timestamp')

        # Append the new data to 'ltc.csv' or create a new file
        initial_df.to_csv('Data/ltc.csv', mode='a', header=not os.path.exists('Data/ltc.csv'), index=True)
        
    # Update initial data to be real-time
    def fetch_real_time_ltc_data(_self):
        try:
            # Set up the end time to the current time
            end_time = datetime.utcnow()

            # Calculate the start time as 1 minute ago
            start_time = end_time - timedelta(minutes=10)

            # Creating request object for current minute's data
            current_request_params = CryptoBarsRequest(
                symbol_or_symbols=["LTC/USD"],
                timeframe=TimeFrame.Minute,
                start=start_time,
                end=end_time
            )

            # Retrieve current minute's data for Bitcoin in a DataFrame
            current_btc_bars = _self.client.get_crypto_bars(current_request_params)
            current_df = current_btc_bars.df
            current_df = current_df.reset_index()
            current_df = current_df.drop(columns=['symbol']).set_index('timestamp')

            # Read existing data from the CSV file
            filename = 'Data/ltc.csv'
            if os.path.isfile(filename):
                existing_data = pd.read_csv(filename, index_col='timestamp')
            else:
                existing_data = pd.DataFrame()

            # Filter out rows with timestamps that already exist in the CSV
            new_rows = current_df[~current_df.index.isin(existing_data.index)]

            # Append new data to 'ltc.csv' only if there are new rows
            if not new_rows.empty:
                # Append value to the file
                new_rows.to_csv(filename, mode='a', header=not os.path.exists(filename))

                # Get the current updated data
                current_data = pd.read_csv(filename, index_col='timestamp')
                
                # Call robot
                _self.price_change_buy("LTC/USD",current_data)
                

        except Exception as e:
            print(f"Error updating LTC data: {e}")
            # Handle the exception as needed


    # Live data from CSV
    def get_live_ltc_data(_self):
        try:
            # Read live data from 'btc.csv' file
            live_data = pd.read_csv('Data/ltc.csv', parse_dates=['timestamp'])
            live_data = live_data.set_index('timestamp')

            return live_data
        except FileNotFoundError:
            print("Error: 'ltc.csv' file not found. Please ensure the file exists.")
            return pd.DataFrame()  # Return an empty DataFrame if the file is not found
        except Exception as e:
            print(f"Error reading ltc live data: {e}")
            return pd.DataFrame()  # Return an empty DataFrame for any other exception
        
    
    ####################### LINK

    # Get initial price data
    def get_initial_link_data(_self):

        # Calculate the start and end times for the initial data (e.g., 30 minutes ago)
        initial_start_time = datetime.utcnow() - timedelta(minutes=30)
        initial_end_time = datetime.utcnow()

        # Creating request object for initial data
        initial_request_params = CryptoBarsRequest(
            symbol_or_symbols=["LINK/USD"],
            timeframe=TimeFrame.Minute,
            start=initial_start_time,
            end=initial_end_time
        )

        # Retrieve initial data for Bitcoin in a DataFrame
        initial_btc_bars = _self.client.get_crypto_bars(initial_request_params)
        initial_df = initial_btc_bars.df
        initial_df = initial_df.reset_index()
        initial_df = initial_df.drop(columns=['symbol']).set_index('timestamp')

        # Append the new data to 'ltc.csv' or create a new file
        initial_df.to_csv('Data/link.csv', mode='a', header=not os.path.exists('Data/link.csv'), index=True)
        
    # Update initial data to be real-time
    def fetch_real_time_link_data(_self):
        try:
            # Set up the end time to the current time
            end_time = datetime.utcnow()

            # Calculate the start time as 1 minute ago
            start_time = end_time - timedelta(minutes=10)

            # Creating request object for current minute's data
            current_request_params = CryptoBarsRequest(
                symbol_or_symbols=["LINK/USD"],
                timeframe=TimeFrame.Minute,
                start=start_time,
                end=end_time
            )

            # Retrieve current minute's data for Bitcoin in a DataFrame
            current_btc_bars = _self.client.get_crypto_bars(current_request_params)
            current_df = current_btc_bars.df
            current_df = current_df.reset_index()
            current_df = current_df.drop(columns=['symbol']).set_index('timestamp')

            # Read existing data from the CSV file
            filename = 'Data/link.csv'
            if os.path.isfile(filename):
                existing_data = pd.read_csv(filename, index_col='timestamp')
            else:
                existing_data = pd.DataFrame()

            # Filter out rows with timestamps that already exist in the CSV
            new_rows = current_df[~current_df.index.isin(existing_data.index)]

            # Append new data to 'link.csv' only if there are new rows
            if not new_rows.empty:
                # Append value to the file
                new_rows.to_csv(filename, mode='a', header=not os.path.exists(filename))

                # Get the current updated data
                current_data = pd.read_csv(filename, index_col='timestamp')
                
                # Call robot
                _self.price_change_buy("LINK/USD",current_data)
                

        except Exception as e:
            print(f"Error updating LINK data: {e}")
            # Handle the exception as needed


    # Live data from CSV
    def get_live_link_data(_self):
        try:
            # Read live data from 'btc.csv' file
            live_data = pd.read_csv('Data/link.csv', parse_dates=['timestamp'])
            live_data = live_data.set_index('timestamp')

            return live_data
        except FileNotFoundError:
            print("Error: 'link.csv' file not found. Please ensure the file exists.")
            return pd.DataFrame()  # Return an empty DataFrame if the file is not found
        except Exception as e:
            print(f"Error reading link live data: {e}")
            return pd.DataFrame()  # Return an empty DataFrame for any other exception
    
    ################################### Calling robots by each price change
        
    # Fetch all robot data
    def fetch_all_robot(_self):
        try:
            # Read data from 'robots.csv'
            robots_data = pd.read_csv('Data/robots.csv')
            return robots_data

        except Exception as e:
            print(f"Error fetching robot data: {e}")
            return None

    # preparing BUY market orders
    def buy(_self, symb, quantity, robot_name):
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
            transactions_data.to_csv('Data/transactions.csv', mode='a', header=not os.path.exists('Data/transactions.csv'), index=False)

        except Exception as e:
            print(f"Error placing buy order: {e}")

    # preparing SELL market orders
    def sell(_self, symb, quantity, robot_name):
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
            transactions_data.to_csv('Data/transactions.csv', mode='a', header=not os.path.exists('Data/transactions.csv'), index=False)

        except Exception as e:
            print(f"Error placing sell order: {e}")
            
    def price_change_buy(_self, crypto, current_data):
        
        # Fetch all robot data outside the loop
        all_robot_data = _self.fetch_all_robot()

        for _, row in all_robot_data.iterrows():
            robot_name = row['Robot Name']
            status = row['Status']
            strategy = row['Stratergy']
            coin = row['Symbol']
            quantity = row['Quantity']

            # Check if the status is "Running" before triggering the strategy
            if coin == crypto: 
                if status == "Running":

                    # Signals initialization
                    buy_condition = False
                    sell_condition = False

                    # Execute the corresponding strategy method
                    if strategy == "SentimentSync":
                        buy_condition, sell_condition = stratergiesClass.SentimentSync(coin,current_data)
                    elif strategy == "SMA":
                        buy_condition, sell_condition = stratergiesClass.sma_strategy(coin,current_data)
                    elif strategy == "RSI":
                        buy_condition, sell_condition = stratergiesClass.rsi_strategy(coin,current_data)
                    elif strategy == "MACD":
                        buy_condition, sell_condition = stratergiesClass.macd_strategy(coin,current_data)
                    elif strategy == "BB":
                        buy_condition, sell_condition = stratergiesClass.bb_strategy(coin,current_data)

                    # Execute buy and sell orders based on signals
                    if buy_condition:

                        # Check if enough money to buy
                        account_info = pd.read_csv("Data/accountInfo.csv", parse_dates=['timestamp'])
                        last_row_cash = account_info['cash'].iloc[-1]
                        last_close_value = current_data.iloc[-1]['close']
                        cost = quantity*last_close_value
                        
                        if last_row_cash >= cost:
                            _self.buy(coin, quantity, robot_name)
                            robotClass.updateBought(quantity,robot_name)
                            print(f"{robot_name} bought")
                        else:
                            print(f"Not enough funds to buy {coin}")

                    elif sell_condition:

                        # Check available quantity before selling
                        position = _self.trading_client.get_open_position(coin.replace("/", ""))
                        available_quantity = float(position.qty_available) if position else 0

                        # Compare available quantity with the quantity the bot wants to sell
                        if available_quantity >= quantity:
                            _self.sell(coin, quantity, robot_name)
                            print(f"{robot_name} sold")
                        else:
                            print(f"Not enough {coin} to sell.")
                    else:
                        print(f"{robot_name}: No buying or selling this round.")     
                else:
                    #Robot is not running
                    print(robot_name + " is not running")
                    continue