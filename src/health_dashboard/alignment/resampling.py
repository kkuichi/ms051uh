import pandas as pd
from health_dashboard.config import RESAMPLE_FREQ, RESAMPLE_FFILL_LIMIT


def resample_hr_1min(
    hr: pd.DataFrame,
    max_ffill_minutes: int = RESAMPLE_FFILL_LIMIT,
) -> pd.DataFrame:
    hr_indexed = hr.set_index("ts_utc")
    resampled = hr_indexed["value"].resample(RESAMPLE_FREQ).mean()
    resampled = resampled.ffill(limit=max_ffill_minutes)

    return resampled.reset_index().rename(columns={"value": "hr_mean"})