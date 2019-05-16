from flask_restful import Resource, reqparse
from models.asset import AssetModel
from utils.finance.returns import calc_returns
from datetime import datetime
import pandas as pd


class AssetReturns(Resource):
    '''
    Calculate % returns for a given asset
    '''

    def get(self, ticker):
        pass
