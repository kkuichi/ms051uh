import pandas as pd
import pytest
from health_dashboard import CSVSchemaError
from health_dashboard.ingestion.validator import (
    validate_hr_schema,
    validate_sleep_schema,
    HR_REQUIRED_COLUMNS,
    SLEEP_REQUIRED_COLUMNS,
)


class TestHRSchemaValidation:
    def test_valid_hr_schema(self):
        df = pd.DataFrame({
            "id": [1],
            "value": [72],
            "unit": ["count/min"],
            "startDate": ["2025-07-23"],
        })

        validate_hr_schema(df)

    def test_missing_required_column_raises(self):
        df = pd.DataFrame({
            "id": [1],
            "value": [72],
            "unit": ["count/min"],
        })

        with pytest.raises(CSVSchemaError, match="Missing required columns"):
            validate_hr_schema(df)

    def test_case_insensitive_column_matching(self):
        df = pd.DataFrame({
            "ID": [1],
            "VALUE": [72],
            "UNIT": ["count/min"],
            "STARTDATE": ["2025-07-23"],
        })

        validate_hr_schema(df)

    def test_all_required_columns_listed_in_constant(self):
        assert HR_REQUIRED_COLUMNS == {"id", "value", "unit", "startDate"}

    def test_multiple_missing_columns(self):
        df = pd.DataFrame({"id": [1]})

        with pytest.raises(CSVSchemaError):
            validate_hr_schema(df)


class TestSleepSchemaValidation:
    def test_valid_sleep_schema(self):
        df = pd.DataFrame({
            "id": [1],
            "value": ["HKCategoryValueSleepAnalysisAsleepCore"],
            "startDate": ["2025-07-23"],
            "endDate": ["2025-07-23"],
        })

        validate_sleep_schema(df)

    def test_missing_required_column_raises(self):
        df = pd.DataFrame({
            "id": [1],
            "value": ["HKCategoryValueSleepAnalysisAsleepCore"],
            "startDate": ["2025-07-23"],
        })

        with pytest.raises(CSVSchemaError, match="Missing required columns"):
            validate_sleep_schema(df)

    def test_case_insensitive_matching(self):
        df = pd.DataFrame({
            "ID": [1],
            "VALUE": ["HKCategoryValueSleepAnalysisAsleepCore"],
            "STARTDATE": ["2025-07-23"],
            "ENDDATE": ["2025-07-23"],
        })

        validate_sleep_schema(df)

    def test_all_required_columns_listed_in_constant(self):
        assert SLEEP_REQUIRED_COLUMNS == {"id", "value", "startDate", "endDate"}