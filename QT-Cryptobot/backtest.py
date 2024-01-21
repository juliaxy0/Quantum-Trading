import pandas as pd
import numpy as np
import vectorbt as vbt

class backtestClass:


    def start_backtest(self, start_date, strategy):

        try:

            # Prepare data
            btc_data = pd.read_csv('backtestingData/BTCUSD.csv', parse_dates=['timestamp'], index_col='timestamp')
            if btc_data.index.duplicated().any():
                btc_data = btc_data[~btc_data.index.duplicated(keep='first')]
            btc_data_resampled = btc_data.resample('T').ffill()
            btc_data_resampled = btc_data_resampled.loc[start_date:]
            btc_close = btc_data_resampled.get('close')

            eth_data = pd.read_csv('backtestingData/ETHUSD.csv', parse_dates=['timestamp'], index_col='timestamp')
            if eth_data.index.duplicated().any():
                eth_data = eth_data[~eth_data.index.duplicated(keep='first')]
            eth_data_resampled = eth_data.resample('T').ffill()
            eth_data_resampled = eth_data_resampled.loc[start_date:]
            eth_close = eth_data_resampled.get('close')

            link_data = pd.read_csv('backtestingData/LINKUSD.csv', parse_dates=['timestamp'], index_col='timestamp')
            if link_data.index.duplicated().any():
                link_data = link_data[~link_data.index.duplicated(keep='first')]
            link_data_resampled = link_data.resample('T').ffill()
            link_data_resampled = link_data_resampled.loc[start_date:]
            link_close = link_data_resampled.get('close')

            ltc_data = pd.read_csv('backtestingData/LTCUSD.csv', parse_dates=['timestamp'], index_col='timestamp')
            if ltc_data.index.duplicated().any():
                ltc_data = ltc_data[~ltc_data.index.duplicated(keep='first')]
            ltc_data_resampled = ltc_data.resample('T').ffill()
            ltc_data_resampled = ltc_data_resampled.loc[start_date:]
            ltc_close = ltc_data_resampled.get('close')

            comb_close = pd.concat([btc_close, eth_close, link_close, ltc_close], axis=1, keys=['BTC/USD', 'ETH/USD', 'LINK/USD', 'LTC/USD'], names=['symbol'])
            comb_close.vbt.drop_levels(-1, inplace=True)

            # Call the corresponding strategy based on the value of strategy
            if strategy == "Simple Moving Average":
                entries, exits = self.SMA(comb_close, fast=500, slow=900)
            elif strategy == "Relative Strength Index":
                entries, exits = self.RSI(comb_close, rsi_window=100, entry=50, exit=20)
            elif strategy == "Moving Average Convergence Divergence":
                entries, exits = self.MACD(comb_close)
            elif strategy == "MACD RSI Synergy":
                entries, exits = self.MACD_RSI(comb_close, 300, 20, 10)
            else:
                # Handle the case when an invalid strategy is provided
                print(f"Invalid strategy: {strategy}")

            pf_kwargs = dict(size=np.inf, fees=0.001, freq='1D')
            pf = vbt.Portfolio.from_signals(comb_close, entries, exits, **pf_kwargs)

            max_return = pf.total_return().groupby('symbol').max()
            max_return_df = max_return.reset_index().set_index('symbol')

            return max_return_df
        
        except Exception as e:
            print(f"Error backtesting datas: {e}")

    def backtest_indv(self, symbol, start_date, strategy):

        try:

            # Prepare data
            btc_data = pd.read_csv(f'backtestingData/{symbol}.csv', parse_dates=['timestamp'], index_col='timestamp')
            if btc_data.index.duplicated().any():
                btc_data = btc_data[~btc_data.index.duplicated(keep='first')]
            btc_data_resampled = btc_data.resample('T').ffill()
            btc_data_resampled = btc_data_resampled.loc[start_date:]
            btc_close = btc_data_resampled.get('close')

            # Call the corresponding strategy based on the value of strategy
            if strategy == "Simple Moving Average":
                entries, exits = self.SMA(btc_close, fast=500, slow=900)
            elif strategy == "Relative Strength Index":
                entries, exits = self.RSI(btc_close, rsi_window=100, entry=50, exit=20)
            elif strategy == "Moving Average Convergence Divergence":
                entries, exits = self.MACD(btc_close)
            elif strategy == "MACD RSI Synergy":
                entries, exits = self.MACD_RSI(btc_close, 300, 20, 10)
            else:
                # Handle the case when an invalid strategy is provided
                print(f"Invalid strategy: {strategy}")

            pf_kwargs = dict(size=np.inf, fees=0.001, freq='1D')
            pf = vbt.Portfolio.from_signals(btc_close, entries, exits, **pf_kwargs)

            stats = pf.stats()
            stats = "\n".join([f"{key}: {value}" for key, value in stats.items()])

            start_value = "${:.2f}".format(pf.stats(metrics="start_value")["Start Value"])
            end_value = "${:.2f}".format(pf.stats(metrics="end_value")["End Value"])
            total_return = "{:.2f}%".format(pf.stats(metrics="total_return")["Total Return [%]"])
            total_trade = pf.stats(metrics="total_trades")["Total Trades"]
            result_array = np.array([start_value, end_value, total_return,total_trade])

            # summary =
            return result_array, stats
        
        except Exception as e:
                print(f"Error backtesting {symbol}: {e}")

################################## Stratergy

    @staticmethod
    def SMA(data, fast, slow):

        try:

            fast_ma = vbt.MA.run(data, fast, short_name='fast')
            slow_ma = vbt.MA.run(data, slow, short_name='slow')

            entries = fast_ma.ma_crossed_above(slow_ma)
            exits = fast_ma.ma_crossed_below(slow_ma)

            return entries, exits
        
        except Exception as e:
            print(f"Error backtesting SMA: {e}")
    
    @staticmethod
    def RSI(data, rsi_window, entry, exit): 

        try:

            rsi = vbt.RSI.run(data, rsi_window, short_name='rsi')
            rsi_above = rsi.rsi_above(entry).to_numpy()
            rsi_below = rsi.rsi_below(exit).to_numpy()

            entries = rsi_above
            exits = rsi_below

            return entries, exits
        
        except Exception as e:
            print(f"Error backtesting RSI: {e}")

    @staticmethod
    def MACD(data):

        try:
            # MACD
            macd = vbt.MACD.run(data,fast_window=620,slow_window=760,signal_window=250, short_name='macd')

            entries = macd.macd_above(macd.signal).to_numpy()
            exits = macd.macd_below(macd.signal).to_numpy()

            return entries, exits

        except Exception as e:
            print(f"Error backtesting MACD : {e}")

    @staticmethod
    def MACD_RSI( data, rsi_window, entry, exit):

        try:

            # RSI
            rsi = vbt.RSI.run(data, rsi_window, short_name='rsi')
            rsi_above = rsi.rsi_above(exit).to_numpy()
            rsi_below = rsi.rsi_below(entry).to_numpy()

            # MACD
            macd = vbt.MACD.run(data, short_name='macd')

            entries = (macd.macd_above(macd.signal)) & rsi_above
            exits = (macd.macd_below(macd.signal)) & rsi_below

            return entries, exits

        except Exception as e:
                print(f"Error backtesting MACD: {e}")
        
        
