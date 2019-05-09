from utils.scraping.browser import open_browser
from selenium.common.exceptions import NoSuchElementException
import requests
from io import StringIO
import pandas as pd
from datetime import datetime, timedelta


class DownloadLinkNotFoundError(Exception):
    def __init__(self, message):
        super().__init__(message)


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
    download_link = browser.find_element_by_css_selector(
        'a[download]').get_attribute('href')

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
        1. ticker:str (eg: 'AAPL')
        2. start:datetime
        3. end:datetime

    - Example
    get_price_history('AAPL') # return all data history until now
    get_price_history('AAPL', start=datetime(2018, 4, 23), end=datetime(2019, 5, 9))
    '''

    # Convert date to timestamps because Yahoo Finance accepts only this format
    start = datetime.timestamp(start)
    end = datetime.timestamp(end + timedelta(days=1))

    # Build the dynamic Asset URL with the corresponding start and end dates
    asset_url = 'https://finance.yahoo.com/quote/{}/history?period1={}&period2={}'.format(
        ticker, start, end)

    try:
        with open_browser(asset_url) as browser:
            cookies = set_cookies(browser)
            download_link = get_download_link(browser)

    except NoSuchElementException:
        raise DownloadLinkNotFoundError(
            'Cannot find the asset download link. Check that you typed a valid ticker name!')

    csv_content = get_csv_content(download_link, cookies)
    price_history_cleaned = clean_csv_content(csv_content)

    return price_history_cleaned
