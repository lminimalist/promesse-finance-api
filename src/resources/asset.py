from flask_restful import Resource, reqparse
from models.asset import AssetModel
from utils.scraping.yahoofinance import get_price_history, DownloadLinkNotFoundError


class Asset(Resource):
    def get(self, ticker):
        '''
        Get the latest price data of an asset from the database

        If the asset does not exist in the DB, it will look for it in Yahoo Finance.
        If the asset exists but not updated, it will fetch for the latest data.
        Else, it will return the results from the database
        '''

        # Tickers are by convention in UPPERCASE
        ticker = ticker.upper()
        asset = AssetModel.objects(ticker=ticker).first()

        if not asset:
            try:
                new_asset = AssetModel(
                    ticker=ticker, price_history=get_price_history(ticker))
            except DownloadLinkNotFoundError:
                return {'message': f'The asset ({ticker}) does not exist in the market yet.'}, 404

            new_asset.save()
            return new_asset.to_json(), 201

        # Check for updates if the asset exists already in the DB
        new_asset_data = asset.check_for_updates()
        if new_asset_data:
            AssetModel.objects(ticker=ticker).update_one(
                push_all__price_history=new_asset_data)
            asset.reload()

        return asset.to_json(), 200
