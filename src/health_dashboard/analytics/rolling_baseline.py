import pandas as pd
from health_dashboard.config import ROLLING_7D_NIGHTS, ROLLING_30D_NIGHTS


def add_rolling_baselines(nightly_df: pd.DataFrame) -> pd.DataFrame:
    df = nightly_df.copy()

    df["roll_7d_deep_hr"] = (
        df["mean_deep"]
        .rolling(window=ROLLING_7D_NIGHTS, min_periods=ROLLING_7D_NIGHTS)
        .mean()
    )

    df["roll_30d_deep_hr"] = (
        df["mean_deep"]
        .rolling(window=ROLLING_30D_NIGHTS, min_periods=ROLLING_30D_NIGHTS)
        .mean()
    )

    return df