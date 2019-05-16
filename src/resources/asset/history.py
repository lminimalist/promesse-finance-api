from flask_restful import Resource, reqparse
from models.asset import AssetModel, asset_schema, price_history_schema
from utils.scraping.yahoofinance import get_price_history, DownloadLinkNotFoundError
from datetime import datetime, date
from time import time
import pandas as pd
from utils.finance.resample import resample_asset
from utils.finance.returns import calc_returns


class AssetHistory(Resource):

    # Define parameters to be used when sending requests to the server
    parser = reqparse.RequestParser()
    parser.add_argument('start', type=str, location='args')
    parser.add_argument('end', type=str, location='args')
    parser.add_argument('time_series', type=str, location='args')
    parser.add_argument('returns', type=int, location='args')

    def get(self, ticker):
        '''
        Get the latest price data of an asset from the database
        '''

        # Tickers are by convention in UPPERCASE
        ticker = ticker.upper()

        # Return error message if asset does not exist
        if not AssetModel.objects(ticker=ticker).first():
            return {'message': f'The asset ({ticker}) does not exist in the database.'}, 404

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
        returns = params['returns'] or None

        # Apply date range parameters
        asset = AssetModel.objects(ticker=ticker).first()
        asset.price_history = filter(
            lambda p:
                p['date'] >= start and p['date'] <= end,
                asset.price_history)

        # Resample asset if times_series paramater is set
        if time_series == 'weekly' or time_series == 'monthly':
            df_price_history = pd.DataFrame(
                asset_schema.dump(asset).data['price_history'])
            df_price_history['date'] = pd.to_datetime(
                df_price_history['date'])
            df_price_history.set_index('date', inplace=True)

            df_price_history_resampled = resample_asset(
                df_price_history, time_series)
            df_price_history_resampled.reset_index(inplace=True)

            df_price_history_resampled['date'] = df_price_history_resampled['date'].astype(
                str)

            asset.price_history = price_history_schema.load(
                df_price_history_resampled.to_dict('records'), many=True)[0]

        if returns:
            df_price_history = pd.DataFrame(
                asset_schema.dump(asset).data['price_history'])
            df_price_history['pct_returns'] = df_price_history['close'].pct_change(
                1)

            print(df_price_history['pct_returns'].describe())

            asset.price_history = price_history_schema.load(
                df_price_history.to_dict('records'), many=True)[0]

        return asset_schema.dump(asset).data, 200

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
        return asset_schema.dump(new_asset).data, 201

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
            return asset_schema.dump(asset).data, 202

        return {'message': f'{ticker} does not need updates.'}, 200
