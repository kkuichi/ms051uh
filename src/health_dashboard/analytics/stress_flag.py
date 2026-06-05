import pandas as pd
from health_dashboard.config import STRESS_DELTA_BPM, STRESS_MIN_CONSECUTIVE_NIGHTS


def add_stress_flag(
    nightly_df: pd.DataFrame,
    delta_bpm: float = STRESS_DELTA_BPM,
    min_consecutive: int = STRESS_MIN_CONSECUTIVE_NIGHTS,
) -> pd.DataFrame:
    df = nightly_df.copy()

    df["deep_vs_7d_delta"] = df["mean_deep"] - df["roll_7d_deep_hr"]

    elevated = df["deep_vs_7d_delta"] >= delta_bpm
    groups = (~elevated).cumsum()
    consecutive_elevated = elevated.groupby(groups).cumsum()

    df["stress_flag"] = consecutive_elevated >= min_consecutive

    return df