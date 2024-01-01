from datetime import datetime
import pandas as pd
import os
import numpy as np
import pandas as pd
import vectorbt as vbt

class backtestClass:

    @staticmethod
    def start_backtest(self, start, strategy):

        try:
            start_date = start

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
            link_close = ltc_data_resampled.get('close')

            comb_close = pd.concat([btc_data, eth_data, link_data, ltc_data], axis=1, keys=['BTC/USD', 'ETH/USD', 'LINK/USD', 'LTC/USD'], names=['symbol'])
            comb_close.vbt.drop_levels(-1, inplace=True)

            # Call the corresponding strategy based on the value of strategy
            if strategy == "SMA":
                entries, exits = self.SMA(comb_close, fast=10, slow=20)
            elif strategy == "RSI":
                entries, exits = self.RSI(comb_close, rsi_window=14, entry=70, exit=30)
            elif strategy == "MACD":
                entries, exits = self.MACD(comb_close, volume_col='volume', entry_threshold=0, exit_threshold=0)
            elif strategy == "BB":
                entries, exits = self.BB(comb_close, window=14, entry_z_score=-1, exit_z_score=1)
            elif strategy == "MACD_RSI":
                entries, exits = self.MACD_RSI(comb_close, 14, 30, 70)
            else:
                # Handle the case when an invalid strategy is provided
                print(f"Invalid strategy: {strategy}")

            pf_kwargs = dict(size=np.inf, fees=0.001, freq='1D')
            pf = vbt.Portfolio.from_signals(comb_close, entries, exits, **pf_kwargs)

            mean_return = pf.total_return().groupby('symbol').mean()
            mean_return_df = mean_return.reset_index().set_index('symbol')
            
            return mean_return_df

        except Exception as e:
                print(f"Error backtesting datas: {e}")

################################## Stratergy

    @staticmethod    
    def SMA(data, fast=10, slow=20):

        try:

            fast_ma = vbt.MA.run(data, fast, short_name='fast')
            slow_ma = vbt.MA.run(data, slow, short_name='slow')

            entries = fast_ma.ma_crossed_above(slow_ma)
            exits = fast_ma.ma_crossed_below(slow_ma)

            return entries, exits
        
        except Exception as e:
            print(f"Error backtesting SMA: {e}")
    
    @staticmethod
    def RSI(data, rsi_window=14, entry=70, exit=30): 

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
    def BB(data, window, entry_z_score=-1, exit_z_score=1):

        try:

            bb = vbt.BB.run(data, window=window, short_name='bb')

            # Calculate z-scores
            z_scores = (data['close'] - bb.bb_lower) / bb.bb_std

            # Generate entry and exit signals based on z-scores
            entries = z_scores < entry_z_score
            exits = z_scores > exit_z_score

            return entries, exits

        except Exception as e:
            print(f"Error backtesting BB: {e}")

    @staticmethod
    def MACD(data):

        try:
            # MACD
            macd = vbt.MACD.run(data, short_name='macd')

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
        
        
