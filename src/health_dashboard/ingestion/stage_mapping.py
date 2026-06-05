import pandas as pd
from health_dashboard.config import STAGE_MAP, ASLEEP_STAGES


def map_stages(df: pd.DataFrame, raw_col: str = "value") -> pd.DataFrame:
    df = df.copy()
    df["stage"] = df[raw_col].map(STAGE_MAP).fillna("Other").astype("category")
    return df


def is_asleep_stage(stage: str) -> bool:
    return stage in ASLEEP_STAGES