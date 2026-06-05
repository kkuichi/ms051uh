import pandas as pd
from health_dashboard.ingestion.stage_mapping import is_asleep_stage


def per_night_sleep_duration(sleep: pd.DataFrame) -> pd.DataFrame:
    """Compute total sleep duration (in seconds) for each night."""
    results = []

    for night_date, night_data in sleep.groupby("night_date"):
        asleep_mask = night_data["stage"].apply(is_asleep_stage)
        total_asleep_s = night_data.loc[asleep_mask, "duration_s"].sum()

        results.append({
            "night_date": night_date,
            "total_sleep_s": total_asleep_s,
        })

    if results:
        df = pd.DataFrame(results).set_index("night_date")
    else:
        df = pd.DataFrame(columns=["total_sleep_s"])
        df.index.name = "night_date"

    return df
