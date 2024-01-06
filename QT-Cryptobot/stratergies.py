import talib
import os
import pandas as pd

class stratergiesClass:

    def __init__(self):
        self.weights = {
            'macd_rsi': 0.5,
            'sentiment': 0.25,
            'prediction': 0.25,
        }

    ################################## CUSTOM STRATERGY
    
    @staticmethod
    def DecisionMaker(coin,current_data):
        try:

            # Get all components
            buy_condition, sell_condition = stratergiesClass.macd_rsi(current_data)
            sentiment_score = stratergiesClass.check_sentiment(coin)
            ml_prediction = stratergiesClass.check_prediction(coin)

            # Calculate based on weightage
            weighted_score = stratergiesClass.calculate_weighted_score(buy_condition, sell_condition, sentiment_score, ml_prediction)

            if buy_condition: 
                if weighted_score >= 0.5:
                    return True, False
                else:
                    return False, False
            if sell_condition: 
                if weighted_score >= 0.5:
                    return False, True
                else:
                    return False, False

        except Exception as e:
            # Handle the exception here, you can print an error message or log it
            print(f"Error in Decision Maker: {e}")

            # Return default values or handle the error as needed
            return False, False

    
    def calculate_weighted_score(self, buy_condition, sell_condition, sentiment_score, ml_prediction):
        
        try:

            # Check if it's a buy condition
            if buy_condition:
                macd_rsi_weighted_score = self.weights['macd_rsi']
                sentiment_weighted_score = self.weights['sentiment']
                prediction_weighted_score = self.weights['prediction']

                # Calculate the weighted score for the buy condition
                weighted_score = (
                    macd_rsi_weighted_score * 1 +  # Assuming buy_condition is True for MACD/RSI
                    sentiment_weighted_score * (sentiment_score >= 5) +
                    prediction_weighted_score * (ml_prediction == 1)
                )
            # Check if it's a sell condition
            elif sell_condition:
                macd_rsi_weighted_score = self.weights['macd_rsi']
                sentiment_weighted_score = self.weights['sentiment']
                prediction_weighted_score = self.weights['prediction']

                # Calculate the weighted score for the sell condition
                weighted_score = (
                    macd_rsi_weighted_score * 0 +  # Assuming buy_condition is False for MACD/RSI
                    sentiment_weighted_score * (sentiment_score <= 5) +
                    prediction_weighted_score * (ml_prediction == 0)
                )
            else:
                # Default to 0 if neither buy_condition nor sell_condition is true
                weighted_score = 0

            return weighted_score

        except Exception as e:
            # Handle the exception here, you can print an error message or log it
            print(f"Error in calculating weighted score: {e}")

            # Return default values or handle the error as needed
            return False, False
        
    @staticmethod
    def macd_rsi(current_data):

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
            print(f"Error in MACD RSI: {e}")

            # Return default values or handle the error as needed
            return False, False
        
    @staticmethod
    def check_sentiment(crypto):
        try:
            # Check if the file exists
            file_path = 'E:/QuantumTrading/QT-API/sentimentData/{}.csv'.format(crypto)
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
            print(f"Exception in check sentiment: {e}")

    @staticmethod
    def check_prediction(symbol):
        try:
            # Specify the file path
            csv_file_path = 'E:/QuantumTrading/QT-API/predictionData/prediction.csv'

            # Check if the file exists
            if os.path.isfile(csv_file_path):
                # Read the CSV file into a DataFrame
                prediction_df = pd.read_csv(csv_file_path)

                # Filter the DataFrame based on the symbol
                symbol_filter = prediction_df['symbol'] == symbol

                # Check if the symbol is present in the DataFrame
                if symbol_filter.any():
                    # Retrieve the prediction value for the specified symbol
                    prediction_value = prediction_df.loc[symbol_filter, 'prediction'].values[0]
                    return prediction_value
                else:
                    print(f"Symbol '{symbol}' not found in the prediction.csv file.")
                    return None
            else:
                print("Prediction file not found.")
                return None
        except Exception as e:
            print(f"An error occurred while checking prediction: {e}")
            return None
        
    ################################## BASIC STRATERGY

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

    