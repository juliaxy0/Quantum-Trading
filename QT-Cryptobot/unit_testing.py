from stratergies import stratergiesClass
import pandas as pd

# FUNCTION 1
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

