from datetime import datetime
import pandas as pd
import os
import requests

# Alpaca
from alpaca.trading.client import TradingClient
from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.timeframe import TimeFrame
from alpaca.data.requests import CryptoBarsRequest

class robotClass:

    def __init__(_self, username):
    
        # Getting user's credentials
        _self.username = username
        api_key, secret_key = _self.get_user_by_username(_self.username)
        API_KEY = api_key
        SECRET_KEY = secret_key

        # Alpaca Trading Client
        _self.trading_client = TradingClient(API_KEY,SECRET_KEY,paper=True)
        _self.client = CryptoHistoricalDataClient()

    def get_user_by_username(_self,username):
        # Replace the URL with your actual API endpoint
        api_url = f"http://127.0.0.1:8000/user/{username}"
        
        # Make a GET request to fetch user data
        response = requests.get(api_url)
        
        if response.status_code == 200:
            user_data = response.json()
            api_key = user_data.get("api_key")
            secret_key = user_data.get("secret_key")
            return api_key, secret_key
        else:
            print(f"Error fetching user data. Status code: {response.status_code}, Details: {response.text}")
            return None
        
    # Function to fetch data and insert into robots.csv
    def create_robot(_self, symbol, quantity, robot_name, strategy, status):
        
        try:

            ########### Robots.csv

            # Create a DataFrame with the provided data
            robot_data = pd.DataFrame({
                'RobotName': [robot_name],
                'Symbol': [symbol],
                'Quantity': [quantity],
                'Strategy': [strategy],
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
                (existing_data['Stratergy'] == strategy)) |
                (existing_data['Robot Name'] == robot_name)
            ].empty:
                print("Error: Robot with the same parameters already exists.")
                return False

            # Append the new data to the 'robots.csv' file or create a new file
            robot_data.to_csv(filename, mode='a', header=not os.path.exists(filename), index=False)
            print("Success: Robot successfully created locally.")

            # Creating in MongoDB
            url = f"http://127.0.0.1:8000/user/{_self.username}/robot/"  # Adjust the URL to include the user ID

            # Data for the new robot
            new_robot_data = {
                "RobotName": robot_name,
                "Symbol": symbol,
                "Quantity": quantity,
                "Strategy": strategy,
                "Status": status,
                "Bought": 0.0,
            }

            try:
                # Make a POST request to create a new robot
                response = requests.post(url, json=new_robot_data)
                response.raise_for_status()  # Raise an exception for HTTP errors

                # Check the response
                if response.status_code == 201:
                    print("Robot created in MongoDB successfully!")
                    print("Created Robot: True")
                else:
                    print(f"Failed to create robot with status code {response.status_code}")
                    print("Response text:", response.text)

            except requests.exceptions.RequestException as e:
                print(f"Error making the request: {e}")

            
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
    
    ############ STEPPED HERE TADI
    @staticmethod
    def deleteRobot(data, selected_robot):
        # Delete the selected robot's row
        data = data[data['Robot Name'] != selected_robot]
        # Save the updated data to the CSV file
        data.to_csv('Data/robots.csv', index=False)

    def updateRobot(_self, data, selected_robot, new_quantity, new_strategy, new_status):
        # Update the data
        data.loc[data['Robot Name'] == selected_robot, 'Quantity'] = new_quantity
        data.loc[data['Robot Name'] == selected_robot, 'Stratergy'] = new_strategy
        data.loc[data['Robot Name'] == selected_robot, 'Status'] = new_status

        # Save the updated data to the CSV file
        data.to_csv('Data/robots.csv', index=False)
        print("Robot data updated localy.")

        # Update robot on mongodb
        url = f"http://127.0.0.1:8000/user/{_self.username}/robot/{selected_robot}"  # Replace with the actual URL of your FastAPI server

        # Data for the robot update
        robot_update_data = {
            "Quantity": new_quantity,
            "Stratergy": new_strategy,
            "Status": new_status,
        }

        try:
            # Make a PUT request to update the robot
            response = requests.put(url, json=robot_update_data)
            response.raise_for_status()  # Raise an exception for HTTP errors

            # Check the response
            if response.status_code == 200:
                print("Robot detail updated to MongoDB successfully!")
                print("Updated Robot:", response.json())
            else:
                print(f"Failed to update robot detail with status code {response.status_code}")
                print("Response text:", response.text)

        except requests.exceptions.RequestException as e:
            print(f"Error making the update detail request: {e}")

    @staticmethod
    def updateBought(quantity, robot_name):
        try:
            # Load the robots data from the CSV file
            robots_data = pd.read_csv('Data/robots.csv')

            # Find the row corresponding to the given robot name
            robot_row = robots_data[robots_data['Robot Name'] == robot_name]

            # Check if the robot exists in the data
            if not robot_row.empty:

                # Get the index of the row
                row_index = robot_row.index[0]

                # Update the 'Bought' column by adding the given quantity
                robots_data.loc[robot_row.index, 'Bought'] += quantity

                # Get the new value of the 'Bought' column
                new_bought_value = robots_data.loc[row_index, 'Bought']

                # Save the updated data back to the CSV file
                robots_data.to_csv('Data/robots.csv', index=False)
                print(f"Bought updated for {robot_name} locally.")

                url = "http://127.0.0.1:8000/robot/"  # Replace with the actual URL of your FastAPI server
                robot_name_to_update = robot_name  # Replace with the RobotName of the robot you want to update

                # Data for the robot update
                robot_update_data = {
                    "Bought": new_bought_value
                }

                try:
                    # Make a PUT request to update the robot
                    response = requests.put(f"{url}/{robot_name_to_update}", json=robot_update_data)
                    response.raise_for_status()  # Raise an exception for HTTP errors

                    # Check the response
                    if response.status_code == 200:
                        print("Robot bought updated in MongoDB successfully!")
                        print("Updated Robot:", response.json())
                    else:
                        print(f"Failed to update robot bought with status code {response.status_code}")
                        print("Response text:", response.text)

                except requests.exceptions.RequestException as e:
                    print(f"Error making the bought request: {e}")

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




