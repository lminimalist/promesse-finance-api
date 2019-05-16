import pandas as pd

resampling_config = {
    'open': lambda x: x[0],
    'high': 'max',
    'low': 'min',
    'close': lambda x: x[-1],
    'volume': 'sum'
}


def resample_monthly(df):
    return df.resample('BMS').agg(resampling_config)


def resample_weekly(df):
    result = df.resample('W').agg(resampling_config)
    result.index += pd.DateOffset(days=-6)

    return result


def resample_asset(df, time_series):
    resample_dict = {
        'weekly': resample_weekly(df),
        'monthly': resample_monthly(df)
    }
    return resample_dict.get(time_series, 'Resampling should be weekly or monthly')
