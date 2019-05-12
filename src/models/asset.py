from mongoengine import *
from datetime import datetime, timedelta
from utils.scraping.yahoofinance import get_price_history


class PriceHistoryModel(EmbeddedDocument):
    date = DateTimeField(primary_key=True)
    open = FloatField(required=True)
    high = FloatField(required=True)
    low = FloatField(required=True)
    close = FloatField(required=True)
    volume = IntField(required=True)


class AssetModel(Document):
    ticker = StringField(required=True)
    category = StringField(default='')
    price_history = ListField(EmbeddedDocumentField(PriceHistoryModel))

    def check_for_updates(self):
        '''
        Check if an asset needs to be updated with the  latest market data
        '''

        # Fetch latest price in db to check against
        latest_date_db = self.price_history[-1]['date']

        # Stock market is closed during weekends
        # If current day is saturday or sunday, no need to fetch for updates
        # To do so, reset to the nearest friday date

        # Set time zone to New York
        recent_date = datetime.utcnow() - timedelta(hours=4)
        # Get the # of the current day
        weekday = recent_date.weekday()
        if weekday == 5:  # Saturday
            recent_date -= timedelta(days=1)
        elif weekday == 6:  # Sunday
            recent_date = timedelta(days=2)

        if latest_date_db != recent_date:
            try:
                updated_data = get_price_history(
                    self.ticker, start=latest_date_db)[1:]

                return updated_data
            except:
                return None

    def to_json(self):
        return {
            f'{self.ticker}': {
                'type': self.category,
                'price_history': [{'date': p.date.strftime("%Y-%m-%d"), 'open': p.open, 'high': p.high, 'low': p.low,
                                   'close': p.close, 'volume': p.volume} for p in self.price_history]
            }
        }

    meta = {
        'collection': 'assets'
    }
