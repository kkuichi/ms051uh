import pandas as pd
from health_dashboard.config import (
    DIPPING_BASELINE_WINDOW,
    DIPPING_MIN_BASELINE_SAMPLES,
    DIPPING_HEALTHY_THRESHOLD_PCT,
    DIPPING_REDUCED_THRESHOLD_PCT,
)


def per_night_dipping(
    hr: pd.DataFrame,
    sleep: pd.DataFrame,
    aligned_hr: pd.DataFrame,
) -> pd.DataFrame:
    results = []

    for night_date, night_data_aligned in aligned_hr.groupby("night_date"):
        night_sleep = sleep[sleep["night_date"] == night_date]

        asleep_mask = night_sleep["stage"].isin(["Core", "Deep", "REM"])

        if not asleep_mask.any():
            results.append({
                "night_date": night_date,
                "baseline_pre_sleep_hr": None,
                "dip_pct": None,
                "dip_classification": "N/A",
            })
            continue

        first_asleep_start = night_sleep.loc[asleep_mask, "start_utc"].min()

        baseline_start = first_asleep_start - DIPPING_BASELINE_WINDOW
        baseline_mask = (
            (hr["ts_utc"] >= baseline_start)
            & (hr["ts_utc"] < first_asleep_start)
        )
        baseline_samples = hr.loc[baseline_mask, "value"]

        if len(baseline_samples) < DIPPING_MIN_BASELINE_SAMPLES:
            results.append({
                "night_date": night_date,
                "baseline_pre_sleep_hr": None,
                "dip_pct": None,
                "dip_classification": "N/A",
            })
            continue

        baseline_hr = baseline_samples.mean()

        deep_mask = night_data_aligned["stage"] == "Deep"

        if not deep_mask.any():
            results.append({
                "night_date": night_date,
                "baseline_pre_sleep_hr": baseline_hr,
                "dip_pct": None,
                "dip_classification": "N/A",
            })
            continue

        deep_mean_hr = night_data_aligned.loc[deep_mask, "value"].mean()
        dip_pct = ((baseline_hr - deep_mean_hr) / baseline_hr) * 100

        if dip_pct >= DIPPING_HEALTHY_THRESHOLD_PCT:
            classification = "healthy"
        elif dip_pct >= DIPPING_REDUCED_THRESHOLD_PCT:
            classification = "reduced"
        else:
            classification = "non-dipper"

        results.append({
            "night_date": night_date,
            "baseline_pre_sleep_hr": baseline_hr,
            "dip_pct": dip_pct,
            "dip_classification": classification,
        })

    if results:
        df = pd.DataFrame(results).set_index("night_date")
    else:
        df = pd.DataFrame(
            columns=[
                "baseline_pre_sleep_hr",
                "dip_pct",
                "dip_classification",
            ]
        )
        df.index.name = "night_date"

    return df