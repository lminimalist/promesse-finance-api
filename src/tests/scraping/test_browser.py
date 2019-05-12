from pytest import mark
import os
from utils.scraping.browser import open_browser
from selenium.webdriver.chrome.webdriver import WebDriver


@mark.browser
def test_chromedriver_in_right_directory():
    '''
    Test if the chromedriver file is in the right directory
    '''
    assert os.path.isfile(f'src/utils/scraping/chromedriver')


@mark.browser
def test_browser_is_created():
    '''
    Test if the browser is created using Selenium
    '''
    with open_browser() as browser:
        assert isinstance(browser, WebDriver)
