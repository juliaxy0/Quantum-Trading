import pandas as pd
import streamlit as st
import yfinance 
import ta
from ta import add_all_ta_features
from ta.utils import dropna

import os


# file upload behavior to change
st.set_option('deprecation.showfileUploaderEncoding', False)


@st.cache_data(show_spinner=False)
def load_data():
    try:
        # Replace the URL with the actual URL of the webpage
        url = 'https://finance.yahoo.com/crypto'

        # Read HTML tables from the webpage
        tables = pd.read_html(url)

        # Assuming the first table contains the data you want
        crypto_data = tables[0]

        components = crypto_data.set_index('Symbol')
        return components

    except Exception as e:
        return pd.DataFrame()  # Return an empty DataFrame in case of an error

@st.cache_data(show_spinner=False)
def load_quotes(asset):
    return yfinance.download(asset)

def main():
    components = load_data()
    title = st.empty()
    st.sidebar.title("Options")

    def label(symbol):
        a = components.loc[symbol]
        return symbol

    # if st.sidebar.checkbox('View cryptocurrencies list'):
    #     st.dataframe(components[['Name',
    #                              'Price (Intraday)',
    #                              'Change',
    #                              '% Change',
    #                              'Market Cap']])

    st.sidebar.subheader('Select asset')
    asset = st.sidebar.selectbox('Click below to select a new asset',
                                 components.index.sort_values(), index=3,
                                 format_func=label)

    title.title(components.loc[asset].Name)
    if st.sidebar.checkbox('View cryptocurrencies info'): #, True
        st.table(components.loc[asset])
    data0 = load_quotes(asset)
    data = data0.copy().dropna()
    data.index.name = None

    section = st.sidebar.slider('Number of quotes', min_value=30,
                        max_value=min([2000, data.shape[0]]),
                        value=500,  step=10)

    data2 = data[-section:]['Adj Close'].to_frame('Adj Close')
    data3 = data.copy()
    data3 = ta.add_all_ta_features(data3, "Open", "High", "Low", "Close", "Volume", fillna=True)
    momentum = data3[['momentum_rsi', 'momentum_roc', 'momentum_tsi', 'momentum_uo', 'momentum_stoch', 'momentum_stoch_signal', 'momentum_wr', 'momentum_ao', 'momentum_kama']]
    volatility = data3[['volatility_atr','volatility_bbm','volatility_bbh','volatility_bbl','volatility_bbw','volatility_bbp','volatility_bbhi','volatility_bbli','volatility_kcc','volatility_kch','volatility_kcl','volatility_kcw','volatility_kcp','volatility_kchi','volatility_kcli','volatility_dcl','volatility_dch',]]
    sma = st.sidebar.checkbox('SMA')

    if sma:
        period= st.sidebar.slider('SMA period', min_value=5, max_value=500,
                             value=20,  step=1)
        data[f'SMA {period}'] = data['Adj Close'].rolling(period ).mean()
        data2[f'SMA {period}'] = data[f'SMA {period}'].reindex(data2.index)

    sma2 = st.sidebar.checkbox('SMA2')
    if sma2:
        period2= st.sidebar.slider('SMA2 period', min_value=5, max_value=500,
                             value=100,  step=1)
        data[f'SMA2 {period2}'] = data['Adj Close'].rolling(period2).mean()
        data2[f'SMA2 {period2}'] = data[f'SMA2 {period2}'].reindex(data2.index)




    st.header(f'Line Chart')
    st.line_chart(data2)

    if st.sidebar.checkbox('View momentum indicators'):

        st.header(f'Momentum Indicators')
        transpose = momentum.iloc[[-5, -4, -3, -2, -1]].transpose()
        st.table(transpose.style.background_gradient(cmap='Blues', axis=1))
        for col in momentum.columns:
            st.subheader(f'Momentum Indicator: {col}')
            st.line_chart(data3[-section:][col].to_frame(col))

    if st.sidebar.checkbox('View volatility indicators'):
        # st.subheader('Apply Technical Indicators')
        # st.code("""
        # data = ta.add_all_ta_features(data3, "Open", "High", "Low", "Close", "Volume", fillna=True)
        # """, language="python")
        st.header(f'Volatility Indicators')
        transpose = volatility.iloc[[-5, -4, -3, -2, -1]].transpose()
        st.table(transpose.style.background_gradient(cmap='Blues', axis=1))
        for col in volatility.columns:
            st.subheader(f'Momentum Indicator: {col}')
            st.line_chart(data3[-section:][col].to_frame(col))

    if st.sidebar.checkbox('View statistic'):
        st.subheader('Statistic')
        st.table(data2.describe())

    if st.sidebar.checkbox('View quotes'):
        st.subheader(f'{asset} historical data')
        st.write(data2)


    st.sidebar.title("About")
    st.sidebar.info('This app aims to provide a comprehensive dashbaord to analyse cryptocurrency performance')

if __name__ == '__main__':
    main()