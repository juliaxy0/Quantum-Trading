import talib
import os
import pandas as pd

class stratergiesClass:
        
    @staticmethod
    def macd_rsi(crypto,current_data):

        try:

            # Perform MACD and RSI calculations for all rows
            current_data['macd'], current_data['macdsignal'], _ = talib.MACD(current_data['close'], fastperiod=12, slowperiod=26, signalperiod=9)
            current_data['rsi'] = talib.RSI(current_data['close'], timeperiod=14)

            # Get the last row
            last_row = current_data.iloc[-1].copy()

            # Get crypto
            crypto = crypto
            crypto = crypto.replace("/USD", "")
            
            # Generate buy/sell signals based on MACD and RSI for the last row only
            last_row['buy_signal'] = (last_row['macd'] > last_row['macdsignal']) & (last_row['rsi'] < 30) 
            last_row['sell_signal'] = (last_row['macd'] < last_row['macdsignal']) & (last_row['rsi'] > 70) 

            buy_condition = last_row['buy_signal']
            sell_condition = last_row['sell_signal']

            # Return buy and sell signals for new rows only
            return buy_condition, sell_condition

        except Exception as e:
            # Handle the exception here, you can print an error message or log it
            print(f"Error in SentimentSync: {e}")

            # Return default values or handle the error as needed
            return False, False
        
    @staticmethod
    def check_sentiment(crypto):
        try:
            # Check if the file exists
            file_path = 'E:/QuantumTrading/QT-Sentiment-API/sentimentData/{}.csv'.format(crypto)
            if not os.path.isfile(file_path):
                print("Error {}: File does not exist.".format(crypto))

            # Read the CSV file into a DataFrame
            df = pd.read_csv(file_path)

            # Check if the DataFrame has at least 10 rows
            if len(df) < 10:
                print("Error {}: Not enough rows in the DataFrame.".format(crypto))

            # Extract the 'Sentiment' column from the last 20 rows
            last_10_sentiments = df.tail(10)['Sentiment']

            # Check if at least 10 out of the last 20 rows have a positive sentiment
            positive_sentiments = last_10_sentiments[last_10_sentiments == 'POSITIVE']

            score = len(positive_sentiments)
            return score

        except Exception as e:
            # Print or log the exception details
            print(f"Exception: {e}")

    @staticmethod
    def sma_strategy(current_data):
        try:
            # SMA (Simple Moving Average)
            current_data['sma'] = talib.SMA(current_data['close'], timeperiod=20)

            # Get the last row
            last_row = current_data.iloc[-1].copy()

            # Generate buy/sell signals based on SMA for the last row only
            last_row['buy_signal'] = last_row['close'] > last_row['sma']
            last_row['sell_signal'] = last_row['close'] < last_row['sma']

            buy_condition = last_row['buy_signal']
            sell_condition = last_row['sell_signal']

            # Return buy and sell signals for new rows only
            return buy_condition, sell_condition

        except Exception as e:
            # Handle the exception here, you can print an error message or log it
            print(f"Error in sma_strategy: {e}")

            # Return default values or handle the error as needed
            return False, False

    @staticmethod
    def rsi_strategy(current_data):
        try:
            # RSI (Relative Strength Index)
            current_data['rsi'] = talib.RSI(current_data['close'], timeperiod=14)

            # Get the last row
            last_row = current_data.iloc[-1].copy()

            # Generate buy/sell signals based on RSI for the last row only
            last_row['buy_signal'] = last_row['rsi'] < 30
            last_row['sell_signal'] = last_row['rsi'] > 70

            buy_condition = last_row['buy_signal']
            sell_condition = last_row['sell_signal']

            # Return buy and sell signals for new rows only
            return buy_condition, sell_condition

        except Exception as e:
            # Handle the exception here, you can print an error message or log it
            print(f"Error in rsi_strategy: {e}")

            # Return default values or handle the error as needed
            return False, False

    @staticmethod
    def macd_strategy(current_data):
        try:
            # MACD (Moving Average Convergence Divergence)
            current_data['macd'], current_data['macdsignal'], _ = talib.MACD(current_data['close'], fastperiod=12, slowperiod=26, signalperiod=9)

            # Get the last row
            last_row = current_data.iloc[-1].copy()

            # Generate buy/sell signals based on MACD for the last row only
            last_row['buy_signal'] = last_row['macd'] > last_row['macdsignal']
            last_row['sell_signal'] = last_row['macd'] < last_row['macdsignal']

            buy_condition = last_row['buy_signal']
            sell_condition = last_row['sell_signal']

            # Return buy and sell signals for new rows only
            return buy_condition, sell_condition

        except Exception as e:
            # Handle the exception here, you can print an error message or log it
            print(f"Error in macd_strategy: {e}")

            # Return default values or handle the error as needed
            return False, False

    @staticmethod
    def bb_strategy(current_data):
        try:
            # Bollinger Bands
            current_data['upper_band'], current_data['middle_band'], current_data['lower_band'] = talib.BBANDS(current_data['close'], timeperiod=20, nbdevup=2, nbdevdn=2)

            # Get the last row
            last_row = current_data.iloc[-1].copy()

            # Generate buy/sell signals based on Bollinger Bands for the last row only
            last_row['buy_signal'] = last_row['close'] < last_row['lower_band']
            last_row['sell_signal'] = last_row['close'] > last_row['upper_band']

            buy_condition = last_row['buy_signal']
            sell_condition = last_row['sell_signal']

            # Return buy and sell signals for new rows only
            return buy_condition, sell_condition

        except Exception as e:
            # Handle the exception here, you can print an error message or log it
            print(f"Error in bb_strategy: {e}")

            # Return default values or handle the error as needed
            return False, False 

    