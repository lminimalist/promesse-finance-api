from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
from contextlib import contextmanager


@contextmanager
def open_browser(url=None, *, headless=True):
    '''
    # Description
    Create a chrome headless browser with Selenium

    # Parameters
    - url (optional)
    - headless (optional): go headless or open a browser window

    # Examples
    with open_browser('http://www.google.com') as browser:
        print(browser.page_source)

    with open_browser('http://www.google.com', headless=False) as browser: # Open browser window
        # Your code
    '''
    options = Options()
    options.headless = headless
    browser = webdriver.Chrome(
        options=options, executable_path=rf'{os.getcwd()}/src/utils/scraping/chromedriver')

    if url:
        browser.get(url)

    yield browser

    browser.close()
