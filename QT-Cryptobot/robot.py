from datetime import datetime
import pandas as pd
import os

# Alpaca
from alpaca.trading.client import TradingClient
from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.timeframe import TimeFrame
from alpaca.data.requests import CryptoBarsRequest

# Configuration
from config import *

class robotClass:

    def __init__(_self):
    
        # Alpaca Trading Client
        _self.trading_client = TradingClient(API_KEY,SECRET_KEY,paper=True)
        _self.client = CryptoHistoricalDataClient()

    # Function to fetch data and insert into robots.csv
    def create_robot(_self, symbol, quantity, robot_name, stratergy, status):
        
        try:

            ########### Robots.csv

            # Create a DataFrame with the provided data
            robot_data = pd.DataFrame({
                'Robot Name': [robot_name],
                'Symbol': [symbol],
                'Quantity': [quantity],
                'Stratergy': [stratergy],
                'Status': [status],
                'Bought': [0.0]
            })

            # Read existing data from the CSV file
            filename = 'Data/robots.csv'
            if os.path.isfile(filename):
                existing_data = pd.read_csv(filename)
            else:
                existing_data = pd.DataFrame()

            # Check if a row with the same values already exists
            if not existing_data[
                ((existing_data['Symbol'] == symbol) &
                (existing_data['Stratergy'] == stratergy)) |
                (existing_data['Robot Name'] == robot_name)
            ].empty:
                print("Error: Robot with the same parameters already exists.")
                return False

            # Append the new data to the 'robots.csv' file or create a new file
            robot_data.to_csv(filename, mode='a', header=not os.path.exists(filename), index=False)
            
            ########### profit.csv

            formatted_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

            # Create a DataFrame with the provided data
            robot_profit = pd.DataFrame({
                'Robot Name': [robot_name],
                'Profit': [0],
                'Timestamp': [formatted_time],
            })

            # Append the new data to the 'robots.csv' file or create a new file
            robot_profit.to_csv('Data/profit.csv', mode='a', header=not os.path.exists('Data/profit.csv'), index=False)
            
            return True

        except Exception as e:
            print(f"Error creating robot: {e}")
            return False
    
    @staticmethod
    def updateBought(quantity, robot_name):
        try:
            # Load the robots data from the CSV file
            robots_data = pd.read_csv('Data/robots.csv')

            # Find the row corresponding to the given robot name
            robot_row = robots_data[robots_data['Robot Name'] == robot_name]

            # Check if the robot exists in the data
            if not robot_row.empty:
                # Update the 'Bought' column by adding the given quantity
                robots_data.loc[robot_row.index, 'Bought'] += quantity

                # Save the updated data back to the CSV file
                robots_data.to_csv('Data/robots.csv', index=False)
                print(f"Bought updated for {robot_name}.")
            else:
                print(f"Robot '{robot_name}' not found.")

        except Exception as e:
            print(f"Error updating 'Bought': {e}")

    @staticmethod
    def updateProfit():
        try:
            # Load robots data from 'Data/robots.csv'
            robots_data = pd.read_csv('Data/robots.csv')

            # Load asset data from 'Data/asset.csv'
            asset_data = pd.read_csv('Data/asset.csv')

            # Adjust the 'Symbol' format in robots_data
            robots_data['Symbol'] = robots_data['Symbol'].str.replace('/', '')

            # Merge robots_data with asset_data based on the modified 'Symbol' column
            merged_data = pd.merge(robots_data, asset_data, left_on='Symbol', right_on='Symbol', how='inner')

            # Convert the 'Price' column to numeric after removing '$' and commas
            merged_data['Price'] = pd.to_numeric(merged_data['Price'].replace('[\$,]', '', regex=True))

            # Calculate profit for each robot
            merged_data['Profit'] = merged_data['Bought'] * merged_data['Price']

            # Create a DataFrame with 'Robot Name', 'Profit', and 'Timestamp'
            profit_data = pd.DataFrame({
                'Robot Name': merged_data['Robot Name'],
                'Profit': merged_data['Profit'],
                'Timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] 
            })

            # Append profit_data to 'Data/profit.csv'
            profit_data.to_csv('Data/profit.csv', mode='a', header=not os.path.exists('Data/profit.csv'), index=False)
        except Exception as e:
            print(f"Error updating profit: {e}")

    # Get historical price data
    def get_historical_data(_self, start_date_str, end_date_str):
        # Define symbols locally
        symbols = ['BTC/USD', 'ETH/USD', 'LINK/USD', 'LTC/USD']

        for symbol in symbols:
            # Remove the '/' in the symbol for the filename
            clean_symbol = symbol.replace('/', '')

            # Empty the file
            file_path = f'E:/QuantumTrading/QT-Backtest-API/backtestingData/{clean_symbol}.csv'
            header = "timestamp,open,high,low,close,volume,trade_count,vwap\n"
            with open(file_path, 'w') as file:
                file.write(header)

            try:
                # Convert input start_date and end_date to datetime objects
                start_date = datetime.strptime(start_date_str, "%d-%m-%Y")
                end_date = datetime.strptime(end_date_str, "%d-%m-%Y")

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

                # Append the new data to 'symbol.csv' or create a new file
                history_filename = f'E:/QuantumTrading/QT-Backtest-API/backtestingData/{clean_symbol}.csv'
                historical_df.to_csv(history_filename, mode='a', header=not os.path.exists(history_filename), index=True)
                print(f"Historical data for {symbol} saved successfully!")

            except Exception as e:
                print(f"Error fetching historical data for {symbol}: {e}")




