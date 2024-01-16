from datetime import datetime, timedelta, timezone
import pandas as pd
import os
import csv
import requests

# Alpaca
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame

# Import classes
from stratergies import stratergiesClass

# TODO : get files method, dont let view read directly

class alpacaClass:

    def __init__(_self, id):

        _self.id = id
        # Getting user's credentials
        _self.password, _self.username, _self.api_key, _self.secret_key = _self.get_user_by_username(_self.id)
        # Alpaca Trading Client
        _self.trading_client = TradingClient(_self.api_key, _self.secret_key, paper=True)
        _self.client = CryptoHistoricalDataClient()
        _self.account = _self.trading_client.get_account()
        
        # Real time data files
        _self.initializeFiles()

        # Fetch initial real time data
        _self.get_initial_btc_data()
        _self.get_initial_eth_data()
        _self.get_initial_ltc_data()
        _self.get_initial_link_data()
        _self.getAccountDetails()

    #################################### home.py
        
    def add_log(_self,log_message):
        try:
            file_path='E:/QuantumTrading/QT-Cryptobot/logs.csv'
            # Append the log message to the CSV file
            with open(file_path, 'a') as file:
                file.write(f"{log_message}\n")

        except Exception as e:
            print(f"Error adding log: {e}")

    def get_user_by_username(_self,id):
        # Replace the URL with your actual API endpoint
        api_url = f"http://127.0.0.1:8000/user/{id}"
        
        # Make a GET request to fetch user data
        response = requests.get(api_url, timeout=30)
        
        if response.status_code == 200:
            user_data = response.json()
            password = user_data.get("password")
            username = user_data.get("username")
            api_key = user_data.get("api_key")
            secret_key = user_data.get("secret_key")
            return password, username, api_key, secret_key
        else:
            print(f"Error fetching user data. Status code: {response.status_code}, Details: {response.text}")
            return None
    
    def update_user_details(_self, password, api_key, secret_key):
        api_url = f"http://127.0.0.1:8000/user/{_self.id}"

        try:

            user_update = {"password": password, "api_key": api_key, "secret_key": secret_key}

            response = requests.put(api_url, json=user_update, timeout=30)
            if response.status_code == 200:
                return True
            else:
                print(f"Failed to update user details. Status code: {response.status_code}, Details: {response.text}")
                return False
        except Exception as e:
            print(f"Error occurred: {e}")
            return False
    
    def continuousMethods(_self):
        _self.fetch_real_time_btc_data()
        _self.fetch_real_time_eth_data()
        _self.fetch_real_time_ltc_data()
        _self.fetch_real_time_link_data()
        _self.getAccountDetails()
        _self.get_asset()

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

            # Create a new row list
            new_row = [current_time, bp, equity, cash, pnl]

            file_path = 'Data/accountInfo.csv'

            # Check if the file exists
            file_exists = os.path.exists(file_path)

            # Append the new row to the CSV file
            with open(file_path, 'a', newline='') as csvfile:
                csv_writer = csv.writer(csvfile)

                # Write the header only if the file is empty
                if not file_exists:
                    header = ['timestamp', 'buying power', 'equity', 'cash', 'pnl']
                    csv_writer.writerow(header)

                csv_writer.writerow(new_row)

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
        file_path = 'Data/profit.csv'
        header = "Username,Robot Name,Profit,Timestamp\n"
        with open(file_path, 'w') as file:
            file.write(header)
            
    ####################### BTC

    # Get initial price data
    def get_initial_btc_data(_self):

        # Calculate the start and end times for the initial data (e.g., 30 minutes ago)
        initial_start_time = datetime.utcnow() - timedelta(minutes=700)
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
        
    ####################### ETH

    # Get initial price data
    def get_initial_eth_data(_self):

        # Calculate the start and end times for the initial data (e.g., 30 minutes ago)
        initial_start_time = datetime.utcnow() - timedelta(minutes=700)
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

        
    ####################### LTC

    # Get initial price data
    def get_initial_ltc_data(_self):

        # Calculate the start and end times for the initial data (e.g., 30 minutes ago)
        initial_start_time = datetime.utcnow() - timedelta(minutes=700)
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
            start_time = end_time - timedelta(minutes=30)

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

    
    ####################### LINK

    # Get initial price data
    def get_initial_link_data(_self):

        # Calculate the start and end times for the initial data (e.g., 30 minutes ago)
        initial_start_time = datetime.utcnow() - timedelta(minutes=700)
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
            start_time = end_time - timedelta(minutes=20)

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

    
    ################################### Calling robots by each price change
        
    # Fetch all robot data
    def fetch_all_robot(_self):
        try:
            # Read data from 'robots.csv'
            robots_data = pd.read_csv('Data/robots.csv')
            filtered_data = robots_data[robots_data['id'] == _self.id]
            return filtered_data

        except Exception as e:
            print(f"Error fetching robot data: {e}")
            return None
        
    def get_latest_cash(self):

        try:
            # Path to the accountInfo.csv file
            account_info_path = 'Data/accountInfo.csv'

            # Read the CSV file into a DataFrame
            account_info_df = pd.read_csv(account_info_path)

            # Get the latest cash value
            latest_cash = account_info_df['cash'].iloc[-1]

            return latest_cash
        except Exception as e:
            print(f"Error fetching latest cash : {e}")

    def get_transactions(_self):
        try:
            file_path='E:/QuantumTrading/QT-Cryptobot/Data/transactions.csv'

            # Read transactions from CSV file
            transactions_data = pd.read_csv(file_path)

            return transactions_data

        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found.")
            return pd.DataFrame()  # Return an empty DataFrame if file not found

        except pd.errors.EmptyDataError:
            print(f"Error: File '{file_path}' is empty.")
            return pd.DataFrame()  # Return an empty DataFrame if file is empty

        except Exception as e:
            print(f"Error reading transactions from '{file_path}': {e}")
            return pd.DataFrame()  # Return an empty DataFrame in case of other errors

    def manual_order(_self,symb,quantity,order_type):
        try:

            # Pulling data
            cash = _self.get_latest_cash()
            all_price = _self.getRealTimePrices()
            formatted_symbol = symb.replace('/USD', '').lower()
            symb_price = all_price.loc[all_price['symbol'] == formatted_symbol, 'last_close'].values[0]

            if order_type == 'Buy':
                # Check if can buy
                if cash >= symb_price:
                    _self.buy(symb, quantity, "Manual")
                    print("Manual buy succesful")
                    return True
                else:
                    print("Manual buy unsuccessful: Not enough fund")
                    return False
                    
            else:
                position = _self.trading_client.get_open_position(symb.replace("/", ""))
                available_quantity = float(position.qty_available) if position else 0

                if available_quantity >= quantity:
                    _self.sell(symb, quantity, "Manual")
                    print("Manual sell succesful")
                else:
                    print("Manual buy unsuccessful: Not enough asset")

        except Exception as e:
            print(f"Error placing manual order: {e}")


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
            order_info = {'id': _self.id, 'robot_name': robot_name, 'client_order_id': market_order_data.client_order_id, 'order_id': order_id.id, 'quantity': market_order_data.qty, 'filled_price': order_id.filled_avg_price, 'type': 'Buy'} 
            transactions_data = pd.DataFrame([order_info])
            transactions_data.to_csv('Data/transactions.csv', mode='a', header=not os.path.exists('Data/transactions.csv'), index=False)
            print(f"Robot {robot_name} buy transaction saved locally")

            # Update MongoDB with the transaction
            url = f"http://127.0.0.1:8000/user/{_self.id}/robot/{robot_name}/transaction/"
            
            # Converting to string
            time = str(formatted_time)
            transaction_id = str(order_id.id)
            filled_price = float(order_id.filled_avg_price)

            transaction_data = {
                "time" : time,
                "transaction_id" : transaction_id,
                "quantity": quantity,
                "filled_price": filled_price,
                "type": "Buy",
            }

            try:
                # Make a POST request to add the transaction
                response = requests.post(url, json=transaction_data, timeout=30)
                response.raise_for_status()  # Raise an exception for HTTP errors

                # Check the response
                if response.status_code == 201:
                    print("Buy transaction added to MongoDB successfully!")
                else:
                    print(f"Failed to add buy transaction with status code {response.status_code}")
                    print("Response text:", response.text)

            except requests.exceptions.RequestException as e:
                print(f"Error making the buy transaction request: {e}")

        except Exception as e:
            print(f"Error placing buy order transaction: {e}")

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
            order_info = {'id': _self.id, 'robot_name': robot_name, 'client_order_id': market_order_data.client_order_id, 'order_id': order_id.id, 'quantity': market_order_data.qty, 'filled_price': order_id.filled_avg_price,'type': "sell"} 
            transactions_data = pd.DataFrame([order_info])
            transactions_data.to_csv('Data/transactions.csv', mode='a', header=not os.path.exists('Data/transactions.csv'), index=False)
            print(f"Robot {robot_name} sell transaction saved locally")

            # Update MongoDB with the transaction
            url = f"http://127.0.0.1:8000/user/{_self.id}/robot/{robot_name}/transaction/"
            
            # Converting to string
            time = str(formatted_time)
            transaction_id = str(order_id.id)
            filled_price = float(order_id.filled_avg_price)

            transaction_data = {
                "time" : time,
                "transaction_id" : transaction_id,
                "quantity": quantity,
                "filled_price": filled_price,
                "type": "Sell",
            }

            try:
                # Make a POST request to add the transaction
                response = requests.post(url, json=transaction_data, timeout=30)
                response.raise_for_status()  # Raise an exception for HTTP errors

                # Check the response
                if response.status_code == 201:
                    print("Sell transaction added to MongoDB successfully!")
                else:
                    print(f"Failed to add sell transaction with status code {response.status_code}")
                    print("Response text:", response.text)

            except requests.exceptions.RequestException as e:
                print(f"Error making the sell transaction request: {e}")

        except Exception as e:
            print(f"Error placing sell order: {e}")
            
    def price_change_buy(_self, crypto, current_data):
        
        # Fetch all robot data outside the loop
        all_robot_data = _self.fetch_all_robot()

        for _, row in all_robot_data.iterrows():
            robot_name = row['Robot Name']
            status = row['Status']
            strategy = row['Strategy']
            sentiment = row['Sentiment']
            prediction = row['Prediction']
            coin = row['Symbol']
            quantity = row['Quantity']

            # Check if the status is "Running" before triggering the strategy
            if coin == crypto:
                if status == "Running":

                    # Signals initialization
                    buy_condition = False
                    sell_condition = False

                    # Execute the corresponding strategy method
                    if strategy == "MACD&RSI":
                        buy_condition, sell_condition = stratergiesClass.DecisionMaker(coin,sentiment,prediction,"MACD&RSI",current_data)
                    elif strategy == "SMA":
                        buy_condition, sell_condition = stratergiesClass.DecisionMaker(coin,sentiment,prediction,"SMA",current_data)
                    elif strategy == "RSI":
                        buy_condition, sell_condition = stratergiesClass.DecisionMaker(coin,sentiment,prediction,"RSI",current_data)
                    elif strategy == "MACD":
                        buy_condition, sell_condition = stratergiesClass.DecisionMaker(coin,sentiment,prediction,"MACD",current_data)
                    elif strategy == "BB":
                        buy_condition, sell_condition = stratergiesClass.DecisionMaker(coin,sentiment,prediction,"BB",current_data)

                    # Execute buy and sell orders based on signals
                    if buy_condition:

                        # Check if enough money to buy
                        account_info = pd.read_csv("Data/accountInfo.csv", parse_dates=['timestamp'])
                        last_row_cash = account_info['cash'].iloc[-1]
                        last_close_value = current_data.iloc[-1]['close']
                        cost = quantity*last_close_value
                        
                        if last_row_cash >= cost:
                            _self.buy(coin, quantity, robot_name)
                            # Update quantity bought by robot
                            _self.updateBought("buy", quantity,robot_name)
                            print(f"{robot_name} bought")
                            _self.add_log(f"{robot_name} bought")
                        else:
                            print(f"{robot_name}: Not enough funds to buy {coin}")
                            _self.add_log(f"{robot_name}: Not enough funds to buy {coin}")

                    elif sell_condition:

                        # Check available quantity before selling
                        position = _self.trading_client.get_open_position(coin.replace("/", ""))
                        available_quantity = float(position.qty_available) if position else 0

                        # Compare available quantity with the quantity the bot wants to sell
                        if available_quantity >= quantity:
                            _self.sell(coin, quantity, robot_name)
                            _self.updateBought("sold",quantity,robot_name)
                            print(f"{robot_name} sold")
                            _self.add_log(f"{robot_name} sold")
                        else:
                            print(f"{robot_name}: Not enough {coin} to sell.")
                            _self.add_log(f"{robot_name}: Not enough {coin} to sell.")
                    else:
                        print(f"{robot_name}: No buying or selling.")   
                        _self.add_log(f"{robot_name}: No buying or selling.")  
                else:
                    #Robot is not running
                    print(robot_name + " is not running")
                    _self.add_log(robot_name + " is not running")
                    continue

    def updateBought(_self, status, quantity, robot_name):
        try:
            # Load the robots data from the CSV file
            robots_data = pd.read_csv('Data/robots.csv')

            # Find the row corresponding to the given robot name
            robot_row = robots_data[robots_data['Robot Name'] == robot_name]

            # Check if the robot exists in the data
            if not robot_row.empty:

                if status == "buy":
                    # Update the 'Bought' column by adding the given quantity
                    robots_data.loc[robot_row.index, 'Bought'] += quantity
                else:
                    robots_data.loc[robot_row.index, 'Bought'] -= quantity

                # Get the new value of the 'Bought' column
                new_bought_value = robots_data.loc[robot_row.index[0], 'Bought']

                # Save the updated data back to the CSV file
                robots_data.to_csv('Data/robots.csv', index=False)
                print(f"{status} updated for {robot_name} locally.")

                # Update the 'Bought' field in MongoDB
                username = _self.username
                url = f"http://127.0.0.1:8000/user/{_self.id}/robot/{robot_name}/update_bought"

                # Data for the robot update
                robot_update_data = {
                    "Bought": new_bought_value
                }

                try:
                    # Make a PUT request to update the robot
                    response = requests.put(url, json=robot_update_data, timeout=30)
                    response.raise_for_status()  # Raise an exception for HTTP errors

                    # Check the response
                    if response.status_code == 200:
                        print(f"Robot {status} updated in MongoDB successfully!")
                        print("Updated Robot:", response.json())
                    else:
                        print(f"Failed to update robot {status} with status code {response.status_code}")
                        print("Response text:", response.text)

                except requests.exceptions.RequestException as e:
                    print(f"Error making the {status} request: {e}")

            else:
                print(f"Robot '{robot_name}' not found.")

        except Exception as e:
            print(f"Error updating '{status}': {e}")