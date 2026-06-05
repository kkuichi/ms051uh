import pandas as pd
from health_dashboard.config import LOCAL_TZ
from health_dashboard.alignment.night_grouping import assign_night_date
from health_dashboard.alignment.hr_sleep_join import align_hr_to_stages
from health_dashboard.analytics.stage_stats import per_night_stage_stats
from health_dashboard.analytics.sleep_duration import per_night_sleep_duration
from health_dashboard.analytics.dipping import per_night_dipping
from health_dashboard.analytics.rolling_baseline import add_rolling_baselines
from health_dashboard.analytics.stress_flag import add_stress_flag


def compute_nightly_metrics(
    raw_hr: pd.DataFrame,
    raw_sleep: pd.DataFrame,
    local_tz: str = LOCAL_TZ,
) -> pd.DataFrame:
    raw_hr = raw_hr.sort_values("ts_utc").reset_index(drop=True)
    raw_sleep = raw_sleep.sort_values("start_utc").reset_index(drop=True)

    raw_sleep["night_date"] = assign_night_date(raw_sleep["start_local"])

    aligned_hr = align_hr_to_stages(raw_hr, raw_sleep)

    stage_stats = per_night_stage_stats(aligned_hr)
    sleep_duration = per_night_sleep_duration(raw_sleep)
    dipping = per_night_dipping(raw_hr, raw_sleep, aligned_hr)

    nightly = stage_stats.join([sleep_duration, dipping], how="outer")
    nightly = nightly.sort_index()

    hr_counts = aligned_hr.groupby("night_date").size().to_frame("n_hr_samples")
    sleep_counts = raw_sleep.groupby("night_date").size().to_frame("n_sleep_records")

    nightly = nightly.join([hr_counts, sleep_counts], how="left")

    if "mean_deep" in nightly.columns:
        nightly = add_rolling_baselines(nightly)
        nightly = add_stress_flag(nightly)

    return nightly