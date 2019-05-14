from pytest import mark, raises
from utils.scraping.browser import open_browser
from utils.scraping.yahoofinance import *
from io import StringIO
import pandas as pd
from datetime import datetime


@mark.yahoofinance
class YahooFinanceBotTests():

    def test_yahoo_finance_scraping_steps(self):
        '''
        Test the step by step process to get data from Yahoo Finance
        '''
        with open_browser('https://finance.yahoo.com/quote/AAPL/history?p=AAPL') as browser:
            cookies = set_cookies(browser)
            assert type(cookies) == list
            assert 'name' in cookies[0]

            download_link = get_download_link(browser)
            assert 'https://query1.finance.yahoo.com' in download_link

            csv_content = get_csv_content(download_link, cookies)
            assert isinstance(csv_content, StringIO)

            price_history_cleaned = clean_csv_content(csv_content)
            assert type(price_history_cleaned) == pd.core.frame.DataFrame

    def test_get_price_history(self):
        '''
        Test the validity of the returned data given a valid/invalid ticke name
        '''
        ticker_data = get_price_history('AAPL')

        assert type(ticker_data) == pd.core.frame.DataFrame

        assert len(ticker_data.columns) == 6

        for i, v in enumerate(['date', 'open', 'high', 'low',
                               'close', 'volume']):
            assert v == ticker_data.columns[i]

        with raises(DownloadLinkNotFoundError):
            get_price_history('AAPLs')

    def test_get_price_history_with_date_range(self):
        '''
        Test for a given date range
        '''
        ticker_data = get_price_history(
            'AAPL', start=datetime(2018, 4, 23), end=datetime(2019, 5, 9))

        assert type(ticker_data) == pd.core.frame.DataFrame

        assert ticker_data['date'].iloc[0] == pd.Timestamp(2018, 4, 23)

        assert ticker_data['date'].iloc[-1] == pd.Timestamp(2019, 5, 9)

    def test_get_price_history_with_bad_date_range(self):
        '''
        Should raise error when given a bad range date
        '''
        with raises(DateRangeError):
            # Try date range where start > end
            ticker_data = get_price_history(
                'AAPL', start=datetime(2019, 4, 23), end=datetime(2018, 5, 9))

    def test_get_price_history_empty_content(self):
        '''
        Should raise error when data cannot be found for a given data range (eg. weekends)
        '''
        with raises(NoCSVContentError):
            # Try a date range with zero result (weekend)
            ticker_data = get_price_history(
                'AAPL', start=datetime(2019, 5, 4), end=datetime(2019, 5, 5))

    def test_get_asset_url(self):
        '''
        Should return url with data bound on it
        '''
        asset_url = get_asset_url('AAPL', 893894894, 89389821)

        assert asset_url == 'https://finance.yahoo.com/quote/AAPL/history?period1=893894894&period2=89389821'
