# Lumibot
from lumibot.brokers import Alpaca
from lumibot.traders import Trader
import pandas as pd

# Configuration
from config import ALPACA_CONFIG
from simpan.Robot.logs.robots.MyStratergy import QTStrategy,MACDStrategy

def run_robot2():
    
    robots_data = pd.read_csv('Data/robots.csv')

    broker = Alpaca(ALPACA_CONFIG)

    strategy1 = QTStrategy(
        broker=broker,
        parameters= {
            "symbol": "BTC"
        })

    strategy2 = MACDStrategy(
        broker=broker,
        parameters= {
            "symbol": "BTC"
        })

    # Setting up robot 1
    if __name__ == "__main__":
        trader = Trader(logfile="Robot/logs/robot1.log")
        trader.add_strategy(strategy2)
        trader.run_all()
