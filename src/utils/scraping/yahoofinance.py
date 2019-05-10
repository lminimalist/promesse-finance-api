from utils.scraping.browser import open_browser
from selenium.common.exceptions import NoSuchElementException
import requests
from io import StringIO
import pandas as pd
from datetime import datetime, timedelta


class DownloadLinkNotFoundError(Exception):
    '''
    Raised when asset download link cannot be found on the page
    '''

    def __init__(self, message):
        super().__init__(message)


class DateRangeError(Exception):
    '''
    Raised when trying to use bad date range (eg: start date > end date)
    '''

    def __init__(self, message):
        super().__init__(message)


class NoCSVContentError(Exception):
    '''
    Raised when trying to use bad date range, like start date greater than end date
    '''

    def __init__(self, message):
        super().__init__(message)


def get_asset_url(ticker, start, end):
    '''
    - Description
    Return the exact Yahoo Finance ticker url given a ticker name, a start and end date 
    Start and end should be in timesamps format

    - Parameters
    ticker
    start (timestamp)
    end (timestamp)
    '''
    return 'https://finance.yahoo.com/quote/{}/history?period1={}&period2={}'.format(
        ticker, start, end)


def set_cookies(browser):
    '''
    Get cookie setting from Yahoo and set it in to the browser
    Browser in headless mode needs cookies to work correctly
    '''

    agree_button = browser.find_element_by_name('agree')
    agree_button.click()

    # Get cookies stored in the browser
    cookies = browser.get_cookies()

    # Set the cookies in to the browser session
    for cookie in cookies:
        browser.add_cookie({k: cookie[k] for k in (
            'name', 'value', 'domain', 'path', 'expiry')})

    return cookies


def get_download_link(browser):
    '''
    Scrape Asset CSV link
    '''
    try:
        download_link = browser.find_element_by_css_selector(
            'a[download]').get_attribute('href')

    # This error occurs when the bot cannot find the a href link on the page.
    # That's normal when a wrong ticker is used, Yahoo Finance returns a 404 page error
    except NoSuchElementException:
        raise DownloadLinkNotFoundError(
            'Cannot find the asset download link. Be sure you typed a valid ticker name!')

    return download_link


def get_csv_content(url, cookies):
    '''
    Download Asset CSV content from the URL scraped using get_download_link function
    Cookies are needed to download the csv.
    '''

    # Set the cookies in to the request header
    jar = requests.cookies.RequestsCookieJar()

    for cookie in cookies:
        jar.set(cookie['name'], cookie['value'], domain=cookie['domain'])

    # GET request to download the csv content
    csv_content = requests.get(url, cookies=jar).text

    # Return the content as a String Object so it can be read by Pandas
    return StringIO(csv_content)


def clean_csv_content(csv_content):
    # Read csv file into pandas dataframe
    ticker_data = pd.read_csv(csv_content, sep=',')

    # It checks if the dataframe has empty data
    if len(ticker_data) == 0:
        raise NoCSVContentError(
            'Error while reading the csv file. The dataframe might be empty')

    # Drop 'Adj Close' column
    ticker_data = ticker_data.drop('Adj Close', axis='columns')

    # Rename columns
    cols_rename = {col: col.lower() for col in ticker_data.columns}
    ticker_data = ticker_data.rename(columns=cols_rename)

    # Convert date column to the right type
    ticker_data['date'] = pd.to_datetime(
        ticker_data['date'], format='%Y-%m-%d')

    # Fill any NaN row
    ticker_data = ticker_data.fillna(method='pad')

    # Convert volume values to integer
    ticker_data['volume'] = ticker_data['volume'].astype('int64')

    return ticker_data


def get_price_history(ticker, *, start=datetime(1970, 1, 1), end=datetime.now()):
    '''
    - Description
    Extract historical data price from Yahoo Finance API

    - Result
    Return a pandas dataframe
    Columns: date, open, high, low, close, volume

    - Parameters
        1. ticker name (eg: 'AAPL')
        2. start date (Optional)
        3. end (Optional)

    - Examples
    get_price_history('AAPL') # return all data history until now
    get_price_history('AAPL', start=datetime(2018, 4, 23), end=datetime(2019, 5, 9))
    '''

    # Convert date to timestamps because Yahoo Finance accepts only this format
    # Date should have an offset of 1 day in order to get the right data. That's how Yahoo Finance works
    start = datetime.timestamp(start + timedelta(days=1))
    end = datetime.timestamp(end + timedelta(days=1))

    # Maybe create later a comprehensive function that checks the validity of a date range:
    # eg: weekend, holidays
    if (start > end):
        raise DateRangeError('Start date cannot be greater than end date')

    asset_url = get_asset_url(ticker, start, end)
    with open_browser(asset_url) as browser:
        cookies = set_cookies(browser)
        download_link = get_download_link(browser)

    csv_content = get_csv_content(download_link, cookies)
    price_history_cleaned = clean_csv_content(csv_content)

    return price_history_cleaned
