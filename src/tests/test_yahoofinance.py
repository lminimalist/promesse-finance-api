from pytest import mark
from utils.scraping.browser import open_browser
from utils.scraping.yahoofinance import *
from io import StringIO
import pandas as pd
from datetime import datetime
import pytest


@mark.yahoofinance
def test_yahoofinancebot():
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


@mark.yahoofinance
def test_get_price_history():
    ticker_data = get_price_history('AAPL')

    assert type(ticker_data) == pd.core.frame.DataFrame

    assert len(ticker_data.columns) == 6

    for i, v in enumerate(['date', 'open', 'high', 'low',
                           'close', 'volume']):
        assert v == ticker_data.columns[i]

    with pytest.raises(DownloadLinkNotFoundError):
        get_price_history('AAPLs')


@mark.yahoofinance
def test_get_price_history_with_start_end():
    ticker_data = get_price_history(
        'AAPL', start=datetime(2018, 4, 23), end=datetime(2019, 5, 9))

    assert type(ticker_data) == pd.core.frame.DataFrame
    assert ticker_data['date'].iloc[0] == pd.Timestamp(2018, 4, 23)
    assert ticker_data['date'].iloc[-1] == pd.Timestamp(2019, 5, 9)
