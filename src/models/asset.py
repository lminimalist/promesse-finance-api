from mongoengine import *
from marshmallow_mongoengine import ModelSchema, fields
from collections import OrderedDict
from datetime import datetime, timedelta
from utils.scraping.yahoofinance import get_price_history


class PriceHistoryModel(EmbeddedDocument):
    date = DateTimeField(required=True)
    open = FloatField(required=True)
    high = FloatField(required=True)
    low = FloatField(required=True)
    close = FloatField(required=True)
    volume = IntField(required=True)
    pct_returns = FloatField()


class AssetModel(Document):
    ticker = StringField(required=True)
    category = StringField(default='')
    price_history = ListField(EmbeddedDocumentField(PriceHistoryModel))

    meta = {
        'collection': 'assets'
    }

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
            recent_date -= timedelta(days=2)

        if latest_date_db.strftime('%Y-%m-%d') != recent_date.strftime('%Y-%m-%d'):
            try:
                updated_data = get_price_history(
                    self.ticker, start=latest_date_db).to_dict('records')[1:]
                if len(updated_data) == 0 or updated_data[0]['date'] == latest_date_db:
                    return None

                return updated_data
            except:
                return None


class AssetSchema(ModelSchema):
    class Meta:
        model = AssetModel
        ordered = True


class PriceHistorySchema(ModelSchema):
    class Meta:
        model = PriceHistoryModel
        ordered = True


asset_schema = AssetSchema(exclude=('id',))
price_history_schema = PriceHistorySchema()
