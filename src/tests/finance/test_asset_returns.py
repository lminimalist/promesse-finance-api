from pytest import mark, raises
from utils.finance.returns import *
import pandas as pd


@mark.asset_returns
class AssetReturnsTests:

    def test_calc_asset_daily_returns(self):
        df = pd.read_csv('AAPL.csv', parse_dates=True)
        df['returns'] = daily_returns(df)

        assert df['returns'][0] == 1

    def test_calc_asset_weekly_returns(self):
        pass

    def test_calc_asset_monthly_returns(self):
        pass
