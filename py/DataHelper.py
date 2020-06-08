from pandas_datareader import data as pdr
import pandas as pd
import yfinance as yf
import numpy as np
yf.pdr_override()


class DataHelper:
    @staticmethod
    def get_history(tickers, start_date, end_date):
        def data(ticker):
            return (pdr.get_data_yahoo(ticker, start=start_date, end=end_date))

        tickers_data = map(data, tickers)

        return pd.concat(tickers_data, keys=tickers, names=['Ticker', 'Date'])


    @staticmethod
    def get_history_formatted(tickers, start_date, end_date):
        data = DataHelper.get_history(tickers, start_date, end_date)
        data = data.reset_index()
        data = data.set_index(['Date', 'Ticker']).sort_index()
        close = data['Close']
        weekdays = pd.date_range(start=start_date, end=end_date, freq='B') # all weekdays in the interval
        close = close.reindex(pd.MultiIndex.from_product([weekdays, tickers], names=['Date', 'Ticker']), fill_value=np.NaN)
        close = close.reset_index().pivot(index='Date', columns='Ticker', values='Close')

        extractors = {}
        for ticker in tickers:
            extractors[ticker] = lambda: DataHelper.extract_ticker(ticker, data)

        return data, close, extractors

    @staticmethod
    def extract_ticker(ticker_code, data):
        ticker = data.xs(ticker_code, level='Ticker', drop_level=False).dropna()
        ticker = ticker.reset_index(level=1, drop=True)
        return ticker

def exercite():
    from datetime import datetime as calendar
    data, close, extractors = DataHelper.get_history_formatted(['MSFT', 'AAPL'],
                                     calendar(2016,1,1), calendar(2020, 1, 1))

    print(extractors['MSFT']())
