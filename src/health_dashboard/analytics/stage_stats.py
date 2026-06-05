import pandas as pd


def per_night_stage_stats(aligned_hr: pd.DataFrame) -> pd.DataFrame:
    stats = aligned_hr.groupby(["night_date", "stage"])["value"].agg(
        ["mean", "std"]
    ).unstack(fill_value=None)

    stats.columns = [
        f"{agg}_{stage.lower()}"
        for agg, stage in stats.columns
    ]

    stages = ["core", "deep", "rem"]

    for stage in stages:
        for agg in ["mean", "std"]:
            col = f"{agg}_{stage}"

            if col not in stats.columns:
                stats[col] = None

    column_order = []

    for stage in stages:
        column_order.append(f"mean_{stage}")
        column_order.append(f"std_{stage}")

    column_order = [
        col for col in column_order
        if col in stats.columns
    ]

    stats = stats[column_order]

    return stats