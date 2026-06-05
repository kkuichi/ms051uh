import pandas as pd
from health_dashboard import AlignmentError
from health_dashboard.alignment.night_grouping import assign_night_date


def align_hr_to_stages(
    hr: pd.DataFrame,
    sleep: pd.DataFrame,
) -> pd.DataFrame:
    if not hr["ts_utc"].is_monotonic_increasing:
        raise AlignmentError("HR data must be sorted by ts_utc")

    if not sleep["start_utc"].is_monotonic_increasing:
        raise AlignmentError("Sleep data must be sorted by start_utc")

    aligned = pd.merge_asof(
        hr[["ts_utc", "ts_local", "value"]],
        sleep[["start_utc", "end_utc", "stage"]],
        left_on="ts_utc",
        right_on="start_utc",
        direction="backward",
        allow_exact_matches=True,
    )

    aligned["stage"] = aligned["stage"].astype("object")

    outside_interval = (
        (aligned["ts_utc"] > aligned["end_utc"])
        | aligned["stage"].isna()
    )

    aligned.loc[outside_interval, "stage"] = "Wake/Out-of-sleep"
    aligned["night_date"] = assign_night_date(aligned["ts_local"])

    return aligned[["ts_utc", "ts_local", "value", "stage", "night_date"]]