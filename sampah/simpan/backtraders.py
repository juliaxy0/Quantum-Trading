import backtrader as bt
import pandas as pd
import talib

class MyStrategy(bt.Strategy):

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

    def next(self):

        # Print data
        timestamp = bt.num2date(self.data.datetime[0]).strftime('%Y-%m-%d %H:%M:%S')


        if self.dataclose[0] < self.dataclose[-1]:
            if self.dataclose[-1] < self.dataclose[-2]:
                self.buy()
                # print(f"Buy Signal! Timestamp: {timestamp}, Close Price: {self.dataclose}")
            
        # elif sell_signal:
        #     self.sell()
        #     print(f"Sell Signal! Timestamp: {timestamp}, Close Price: {close_price}")

class MyStrategy1(bt.Strategy):

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

    # def next(self):

    #     # Print data
    #     timestamp = bt.num2date(self.data.datetime[0]).strftime('%Y-%m-%d %H:%M:%S')


    #     if self.dataclose[0] < self.dataclose[-1]:
    #         if self.dataclose[-1] < self.dataclose[-2]:
    #             if self.dataclose[-2] < self.dataclose[-3]:
    #                 self.buy()
                # print(f"Buy Signal! Timestamp: {timestamp}, Close Price: {self.dataclose}")
            
        # elif sell_signal:
        #     self.sell()
        #     print(f"Sell Signal! Timestamp: {timestamp}, Close Price: {close_price}")

if __name__ == "__main__":

    cerebro = bt.Cerebro()

    # Load data from CSV
    df = pd.read_csv('backtestingData/history_btc.csv', parse_dates=True, index_col='timestamp')
    df = df.drop(columns=['trade_count', 'vwap'])
    
    # Load data from CSV and convert 'timestamp' column to datetime
    data = bt.feeds.PandasData(dataname=df,
                               datetime=None,
                               open=0,
                               high=1,
                               low=2,
                               close=3,
                               volume=4,
                               openinterest=-1)

    cerebro.adddata(data)
    cerebro.addstrategy(MyStrategy)
    cerebro.addstrategy(MyStrategy1)


    # # Set our desired cash start
    cerebro.broker.setcash(100000.0)

    # # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # # Run over everything
    cerebro.run()

    # # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # # After cerebro.run()
    returns = cerebro.broker.getvalue() - cerebro.broker.startingcash
    print(f'Total Returns: {returns:.2f} USD')
    print(f'Percentage Returns: {returns / cerebro.broker.startingcash * 100:.2f}%')

    cerebro.plot()
