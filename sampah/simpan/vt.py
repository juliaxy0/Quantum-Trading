import numpy as np
import pandas as pd
import vectorbt as vbt

def MACD_RSI(data, rsi_window, entry, exit):

        # RSI
        rsi = vbt.RSI.run(data, rsi_window, short_name='rsi')
        rsi_above = rsi.rsi_above(exit).to_numpy()
        rsi_below = rsi.rsi_below(entry).to_numpy()

        # MACD
        macd = vbt.MACD.run(data, short_name='macd')

        entries = (macd.macd_above(macd.signal)) & rsi_above
        exits = (macd.macd_below(macd.signal)) & rsi_below

        return entries, exits

def MultipleMA(data):

        fast_ma = vbt.MA.run(data, [100, 200], short_name='fast')
        slow_ma = vbt.MA.run(data, [400, 400], short_name='slow')

        entries = fast_ma.ma_crossed_above(slow_ma)
        exits = fast_ma.ma_crossed_below(slow_ma)

        return entries, exits

# Prepare data
btc_data = pd.read_csv('backtestingData/BTCUSD.csv', parse_dates=['timestamp'], index_col='timestamp')
btc_data['timestamp'] = btc_data.index
btc_data = btc_data.get('close')

eth_data = pd.read_csv('backtestingData/ETHUSD.csv', parse_dates=['timestamp'], index_col='timestamp')
eth_data['timestamp'] = eth_data.index
eth_data = eth_data.get('close')

link_data = pd.read_csv('backtestingData/LINKUSD.csv', parse_dates=['timestamp'], index_col='timestamp')
link_data['timestamp'] = link_data.index
link_data = link_data.get('close')

ltc_data = pd.read_csv('backtestingData/LTCUSD.csv', parse_dates=['timestamp'], index_col='timestamp')
ltc_data['timestamp'] = ltc_data.index
ltc_data = ltc_data.get('close')

comb_price = pd.concat([btc_data, eth_data, link_data, ltc_data], axis=1, keys=['BTC/USD', 'ETH/USD', 'LINK/USD', 'LTC/USD'], names=['symbol'])
comb_price.vbt.drop_levels(-1, inplace=True)

# entries, exits = MACD_RSI(comb_price, 14, 30, 70)
entries, exits = MultipleMA(comb_price)

pf_kwargs = dict(size=np.inf, fees=0.001, freq='1D')
pf = vbt.Portfolio.from_signals(comb_price, entries, exits, **pf_kwargs)

print(pf.total_return())
# mean_return = pf.total_return().groupby('symbol').mean()
# mean_return_df = mean_return.reset_index().set_index('symbol')
# print(mean_return_df)

# pf = vbt.Portfolio.from_signals(eth_data, entries, exits, **pf_kwargs)
# print(pf.stats())

# st.bar_chart(mean_return_df)
# print(pf.orders.records_readable)




