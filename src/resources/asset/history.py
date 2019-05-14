from flask_restful import Resource, reqparse
from models.asset import AssetModel
from utils.scraping.yahoofinance import get_price_history, DownloadLinkNotFoundError
from datetime import datetime, date


class AssetHistory(Resource):
    # Define parameters to be used when sending requests to the server
    parser = reqparse.RequestParser()
    parser.add_argument('start', type=str, location='args')
    parser.add_argument('end', type=str, location='args')
    parser.add_argument('time_series', type=str, location='args')

    def get(self, ticker):
        '''
        Get the latest price data of an asset from the database
        '''

        # Tickers are by convention in UPPERCASE
        ticker = ticker.upper()

        # Setting querystring parameters
        params = self.parser.parse_args()

        try:
            start = datetime.strptime(
                params['start'], '%Y-%m-%d')
        except:
            start = datetime(1900, 1, 1)

        try:
            end = datetime.strptime(params['end'], '%Y-%m-%d')
        except:
            end = datetime.utcnow()

        time_series = params['time_series'] or 'daily'

        # Return error message if asset does not exist
        if not AssetModel.objects(ticker=ticker).first():
            return {'message': f'The asset ({ticker}) does not exist in the database.'}, 404

        # Return asset with applied date range filter
        asset = AssetModel.objects(ticker=ticker).first()
        asset.time_series = time_series
        asset.price_history = filter(
            lambda p:
                p['date'] >= start and p['date'] <= end,
                asset.price_history)

        return asset.to_json(), 200

    def post(self, ticker):
        '''
        Create a new asset from Yahoo Finance
        '''
        try:
            new_asset = AssetModel(
                ticker=ticker, price_history=get_price_history(ticker).to_dict('records'))
        except DownloadLinkNotFoundError:
            return {'message': f'{ticker} does not exist in the market yet.'}, 404

        new_asset.save()
        return new_asset.to_json(), 201

    def put(self, ticker):
        '''
        Create or update an asset to the latest data

        If the asset does not exist in the DB, it will look for it in Yahoo Finance.
        If the asset exists but not updated, it will fetch for the latest data.
        Else, it will return the results from the database
        '''
        ticker = ticker.upper()
        asset = AssetModel.objects(ticker=ticker).first()

        # Create a new asset the DB if it does not exist yet
        if not asset:
            return self.post(ticker)

        # Update the asset (if it does exist) with the latest history price data
        updated_asset_data = asset.check_for_updates()
        if updated_asset_data:
            AssetModel.objects(ticker=ticker).update_one(
                push_all__price_history=updated_asset_data)

            asset.reload()
            return asset.to_json(), 202

        return {'message': f'{ticker} does not need updates.'}, 200
