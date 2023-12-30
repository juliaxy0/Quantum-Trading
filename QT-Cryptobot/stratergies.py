import talib
import requests

class stratergiesClass:
        
    @staticmethod
    def SentimentSync(crypto,current_data):

        try:

            # Perform MACD and RSI calculations for all rows
            current_data['macd'], current_data['macdsignal'], _ = talib.MACD(current_data['close'], fastperiod=12, slowperiod=26, signalperiod=9)
            current_data['rsi'] = talib.RSI(current_data['close'], timeperiod=14)

            # Get the last row
            last_row = current_data.iloc[-1].copy()

            # Get crypto
            crypto = crypto
            crypto = crypto.replace("/USD", "")
            sentiment_result = stratergiesClass.check_sentiment(crypto)

            # Extract buy_condition and error
            result = sentiment_result.get('result', False)

            # Generate buy/sell signals based on MACD and RSI for the last row only
            last_row['buy_signal'] = (last_row['macd'] > last_row['macdsignal']) & (last_row['rsi'] < 30) & (result == True)
            last_row['sell_signal'] = (last_row['macd'] < last_row['macdsignal']) & (last_row['rsi'] > 70) & (result == False)

            buy_condition = last_row['buy_signal']
            sell_condition = last_row['sell_signal']

            # Return buy and sell signals for new rows only
            return buy_condition, sell_condition

        except Exception as e:
            # Handle the exception here, you can print an error message or log it
            print(f"Error in SentimentSync: {e}")

            # Return default values or handle the error as needed
            return False, False
    
    def check_sentiment(crypto):
        try:
            url = f"http://127.0.0.1:8000/check_sentiment/{crypto}"
            response = requests.get(url)
            result = response.json()

            # If problem, default is false
            return {
                'result': result.get('result', False),
                'error': result.get('error', False),
            }
        except Exception as e:
            # Handle the exception here, you can print an error message or log it
            print(f"Error in Sentiment API: {e}")

            # Return default values or handle the error as needed
            return {
                'result': False,
                'error': False,
            }

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

    