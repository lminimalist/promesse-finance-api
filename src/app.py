from utils.scraping.yahoofinance import get_price_history


ticker = get_price_history(
    'AAPL', start='2018-04-23', end='2019-05-10')
print(ticker)
