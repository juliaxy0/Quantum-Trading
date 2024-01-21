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

    def __init__(_self, id):
    
        # Getting user's credentials
        _self.id = id
        # Getting user's credentials
        _self.password, _self.username, _self.api_key, _self.secret_key = _self.get_user_by_username(_self.id)
        

        # Alpaca Trading Client
        _self.trading_client = TradingClient(_self.api_key, _self.secret_key, paper=True)
        _self.client = CryptoHistoricalDataClient()

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
        
    # Function to fetch data and insert into robots.csv
    def create_robot(_self, symbol, quantity, robot_name, strategy, sentiment_analysis, prediction_analysis,status ):
        
        try:

            ########### Robots.csv

            # Create a DataFrame with the provided data
            robot_data = pd.DataFrame({
                'id' : [_self.id],
                'RobotName': [robot_name],
                'Symbol': [symbol],
                'Quantity': [quantity],
                'Strategy': [strategy],
                'Status': [status],
                'Sentiment': [sentiment_analysis],
                'Prediction': [prediction_analysis],
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
                (existing_data['Strategy'] == strategy)) |
                (existing_data['Robot Name'] == robot_name)
            ].empty:
                print("Error: Robot with the same parameters already exists.")
                return False

            # Append the new data to the 'robots.csv' file or create a new file
            robot_data.to_csv(filename, mode='a', header=not os.path.exists(filename), index=False)
            print("Success: Robot successfully created locally.")

            # Creating in MongoDB
            url = f"http://127.0.0.1:8000/user/{_self.id}/robot/"  # Adjust the URL to include the user ID

            # Data for the new robot
            new_robot_data = {
                "RobotName": robot_name,
                "Symbol": symbol,
                "Quantity": quantity,
                "Strategy": strategy,
                'Sentiment': sentiment_analysis,
                'Prediction': prediction_analysis,
                "Status": status,
                "Bought": 0.0,
            }

            try:
                # Make a POST request to create a new robot
                response = requests.post(url, json=new_robot_data, timeout=30)
                response.raise_for_status()  # Raise an exception for HTTP errors

                # Check the response
                if response.status_code == 201:
                    print("Robot created in MongoDB successfully!")
                else:
                    print(f"Failed to create robot with status code {response.status_code}")
                    print("Response text:", response.text)

            except requests.exceptions.RequestException as e:
                print(f"Error making the request: {e}")
            
            return True

        except Exception as e:
            print(f"Error creating robot: {e}")
            return False
    
    def deleteRobot(_self, data, selected_robot):
        # Delete the selected robot's row locally
        data = data[data['Robot Name'] != selected_robot]
        # Save the updated data to the CSV file
        data.to_csv('Data/robots.csv', index=False)
        print("Robot data deleted locally.")

        # Delete the selected robot in MongoDB
        url = f"http://127.0.0.1:8000/user/{_self.id}/robot/{selected_robot}"

        try:
            # Make a DELETE request to remove the robot
            response = requests.delete(url, timeout=30)
            response.raise_for_status()  # Raise an exception for HTTP errors

            # Check the response
            if response.status_code == 200:
                print("Robot deleted from MongoDB successfully!")
            else:
                print(f"Failed to delete robot with status code {response.status_code}")
                print("Response text:", response.text)

        except requests.exceptions.RequestException as e:
            print(f"Error making the delete request: {e}")


    def updateRobot(_self, data, selected_robot, new_quantity, new_strategy, new_status, new_sentiment_analysis, new_prediction_analysis):
        # Update the data
        data.loc[data['Robot Name'] == selected_robot, 'Quantity'] = new_quantity
        data.loc[data['Robot Name'] == selected_robot, 'Strategy'] = new_strategy
        data.loc[data['Robot Name'] == selected_robot, 'Status'] = new_status
        data.loc[data['Robot Name'] == selected_robot, 'Sentiment'] = new_sentiment_analysis
        data.loc[data['Robot Name'] == selected_robot, 'Prediction'] = new_prediction_analysis

        # Save the updated data to the CSV file
        data.to_csv('Data/robots.csv', index=False)
        print("Robot data updated localy.")

        # Update robot on mongodb
        url = f"http://127.0.0.1:8000/user/{_self.id}/robot/{selected_robot}"  # Replace with the actual URL of your FastAPI server

        # Data for the robot update
        robot_update_data = {
            "Quantity": new_quantity,
            "Strategy": new_strategy,
            'Sentiment': new_sentiment_analysis,
            'Prediction': new_prediction_analysis,
            "Status": new_status,
        }

        try:
            # Make a PUT request to update the robot
            response = requests.put(url, json=robot_update_data, timeout=30)
            response.raise_for_status()  # Raise an exception for HTTP errors

            # Check the response
            if response.status_code == 200:
                print("Robot detail updated to MongoDB successfully!")
            else:
                print(f"Failed to update robot detail with status code {response.status_code}")
                print("Response text:", response.text)

        except requests.exceptions.RequestException as e:
            print(f"Error making the update detail request: {e}")

    import pandas as pd

    def get_profit(_self):
        try:

            file_path='Data/profit.csv'

            # Read profit_data from CSV file
            profit_data = pd.read_csv(file_path)

            # Filter the DataFrame to include only rows where Username matches self.username
            filtered_data = profit_data[profit_data['Username'] == _self.username]

            return filtered_data

        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found.")
            return pd.DataFrame()  # Return an empty DataFrame if file not found

        except pd.errors.EmptyDataError:
            print(f"Error: File '{file_path}' is empty.")
            return pd.DataFrame()  # Return an empty DataFrame if file is empty

        except Exception as e:
            print(f"Error reading transactions from '{file_path}': {e}")
            return pd.DataFrame()  # Return an empty DataFrame in case of other errors

    def get_transaction(_self):
        try:

            file_path='Data/transactions.csv'

            # Read transactions from CSV file
            transactions_data = pd.read_csv(file_path)

            # Filter the DataFrame to include only rows where Username matches self.username
            filtered_data = transactions_data[transactions_data['Username'] == _self.username]

            # Optional: You can perform additional processing or filtering if needed

            return filtered_data

        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found.")
            return pd.DataFrame()  # Return an empty DataFrame if file not found

        except pd.errors.EmptyDataError:
            print(f"Error: File '{file_path}' is empty.")
            return pd.DataFrame()  # Return an empty DataFrame if file is empty

        except Exception as e:
            print(f"Error reading transactions from '{file_path}': {e}")
            return pd.DataFrame()  # Return an empty DataFrame in case of other errors

    def updateProfit(_self):
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

            # Calculate profit for each robot using the 'Bought' quantity
            merged_data['Profit'] = merged_data['Bought'] * merged_data['Price']

            # Create a DataFrame with 'Username', 'Robot Name', 'Profit', and 'Timestamp'
            profit_data = pd.DataFrame({
                'id': [_self.id] * len(merged_data),  # Repeat username for each row
                'Robot Name': merged_data['Robot Name'],
                'Profit': merged_data['Profit'],
                'Timestamp': [datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]] * len(merged_data)
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




