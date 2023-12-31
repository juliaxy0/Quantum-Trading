from lumibot.brokers import Alpaca
from lumibot.traders import Trader
import pandas as pd

# Configuration
from config import ALPACA_CONFIG
from robots.MyStratergy import QTStrategy,MACDStrategy

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

trader = Trader()
trader.add_strategy(strategy1)
trader.add_strategy(strategy2)
trader.run_all()




