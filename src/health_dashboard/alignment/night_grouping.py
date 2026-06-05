import pandas as pd


def assign_night_date(ts_local: pd.Series) -> pd.Series:
    if ts_local.dt.tz is None:
        raise ValueError("ts_local must be timezone-aware")

    shifted = ts_local - pd.Timedelta(hours=12)
    night_date = shifted.dt.date
    night_date = pd.to_datetime(night_date) + pd.Timedelta(days=1)

    return night_date.dt.date