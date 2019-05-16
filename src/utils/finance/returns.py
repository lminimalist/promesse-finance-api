import pandas as pd


def daily_returns(df):
    return df['close'].pct_change(1)


def weekly_returns(df):
    return df['close'].pct_change(1)


def monthly_returns(df):
    return df['close'].pct_change(1)


def calc_returns(df, time_series):
    returns_dict = {
        'daily': daily_returns(df),
        'weekly': weekly_returns(df),
        'monthly': monthly_returns(df)
    }
    return returns_dict.get(time_series, 'Returns should be daily, weekly or monthly')
