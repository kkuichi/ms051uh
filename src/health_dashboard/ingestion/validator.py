import pandas as pd
from health_dashboard import CSVSchemaError


HR_REQUIRED_COLUMNS: frozenset[str] = frozenset({"id", "value", "unit", "startDate"})
SLEEP_REQUIRED_COLUMNS: frozenset[str] = frozenset({
    "id",
    "value",
    "startDate",
    "endDate",
})


def validate_hr_schema(df: pd.DataFrame) -> None:
    df_cols_lower = {col.lower(): col for col in df.columns}
    required_lower = {col.lower() for col in HR_REQUIRED_COLUMNS}
    missing = required_lower - set(df_cols_lower.keys())

    if missing:
        raise CSVSchemaError(
            f"Missing required columns in heart rate CSV: {sorted(missing)}. "
            f"Expected: {', '.join(sorted(HR_REQUIRED_COLUMNS))}"
        )


def validate_sleep_schema(df: pd.DataFrame) -> None:
    df_cols_lower = {col.lower(): col for col in df.columns}
    required_lower = {col.lower() for col in SLEEP_REQUIRED_COLUMNS}
    missing = required_lower - set(df_cols_lower.keys())

    if missing:
        raise CSVSchemaError(
            f"Missing required columns in sleep CSV: {sorted(missing)}. "
            f"Expected: {', '.join(sorted(SLEEP_REQUIRED_COLUMNS))}"
        )