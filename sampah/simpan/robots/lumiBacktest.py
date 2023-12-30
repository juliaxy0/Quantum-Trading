import datetime

import pandas as pd
from lumibot.backtesting import BacktestingBroker
from lumibot.data_sources import PandasData
from lumibot.entities import Asset, Data
from lumibot.traders import Trader

# Strategy 
from simpan.Robot.logs.robots.MyStratergy import QTStrategy

# Read the data from the CSV file
df = pd.read_csv(f"backtestingData\history_btc.csv")
df = df.set_index("timestamp")
df.index = pd.to_datetime(df.index)
asset = Asset(
    symbol="BTC",
    asset_type="stock",
)
pandas_data = {}
pandas_data[asset] = Data(
    asset,
    df,
    timestep="minute",
)

# Pick the date range you want to backtest
backtesting_start = datetime.datetime(2023, 1, 1)
backtesting_end = datetime.datetime(2023, 1, 30)
logfile = "logs/test.log"

# Run the backtesting
trader = Trader(backtest=True, logfile=logfile )
data_source = PandasData(
    pandas_data=pandas_data,
    datetime_start=backtesting_start,
    datetime_end=backtesting_end,
)
broker = BacktestingBroker(data_source)
strategy = QTStrategy(
    broker=broker,
    backtesting_start=backtesting_start,
    backtesting_end=backtesting_end,
    budget=100000,
)
trader.add_strategy(strategy)
trader.run_all()