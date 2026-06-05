from io import BytesIO
import pandas as pd
import pytest
from health_dashboard import CSVSchemaError, OOMGuardError
from health_dashboard.ingestion.csv_parser import parse_heart_rate, parse_sleep


class TestParseHeartRate:
    def test_parse_valid_hr_csv(self, heart_rate_sample_csv: BytesIO):
        df, report = parse_heart_rate(heart_rate_sample_csv, filename="test.csv")

        assert len(df) == 10
        assert list(df.columns) == ["id", "value", "unit", "ts_utc", "ts_local"]
        assert report.filename == "test.csv"
        assert report.rows_read == 10
        assert report.rows_dropped_invalid == 0
        assert report.rows_dropped_out_of_range == 0
        assert not report.was_downsampled

    def test_hr_timestamps_sorted_by_utc(self, heart_rate_sample_csv: BytesIO):
        df, _ = parse_heart_rate(heart_rate_sample_csv)

        assert df["ts_utc"].is_monotonic_increasing

    def test_hr_contains_both_utc_and_local_timestamps(self, heart_rate_sample_csv: BytesIO):
        df, _ = parse_heart_rate(heart_rate_sample_csv, local_tz="Europe/Bratislava")

        assert "ts_utc" in df.columns
        assert "ts_local" in df.columns
        assert df["ts_utc"].dt.tz is not None
        assert df["ts_local"].dt.tz is not None

    def test_hr_out_of_range_dropped(self):
        csv_content = b"""id;value;unit;startDate
1;72.0;count/min;2025-07-23 14:39:29 +0100
2;-5.0;count/min;2025-07-23 14:44:15 +0100
3;241.0;count/min;2025-07-23 14:49:02 +0100
4;75.0;count/min;2025-07-23 15:00:30 +0100"""

        buf = BytesIO(csv_content)
        df, report = parse_heart_rate(buf)

        assert len(df) == 2
        assert report.rows_dropped_out_of_range == 2

    def test_missing_columns_raises_error(self):
        csv_content = b"""id;value;unit
1;72.0;count/min"""

        buf = BytesIO(csv_content)
        with pytest.raises(CSVSchemaError):
            parse_heart_rate(buf)

    def test_bom_handled(self):
        csv_content = b"""\xef\xbb\xbfid;value;unit;startDate
1;72.0;count/min;2025-07-23 14:39:29 +0100"""

        buf = BytesIO(csv_content)
        df, _ = parse_heart_rate(buf)

        assert len(df) == 1


class TestParseSleep:
    def test_parse_valid_sleep_csv(self, sleep_sample_csv: BytesIO):
        df, report = parse_sleep(sleep_sample_csv, filename="sleep.csv")

        assert len(df) == 5
        expected_cols = [
            "id",
            "raw_value",
            "stage",
            "start_utc",
            "end_utc",
            "start_local",
            "end_local",
            "duration_s",
        ]
        assert list(df.columns) == expected_cols
        assert report.filename == "sleep.csv"
        assert report.rows_read == 5

    def test_sleep_timestamps_sorted_by_utc(self, sleep_sample_csv: BytesIO):
        df, _ = parse_sleep(sleep_sample_csv)

        assert df["start_utc"].is_monotonic_increasing

    def test_sleep_stages_mapped_correctly(self, sleep_sample_csv: BytesIO):
        df, _ = parse_sleep(sleep_sample_csv)

        stages = df["stage"].unique()
        expected_stages = {"InBed", "Core", "Deep", "REM", "Awake"}
        assert set(stages) == expected_stages

    def test_sleep_duration_computed(self, sleep_sample_csv: BytesIO):
        df, _ = parse_sleep(sleep_sample_csv)

        assert (df["duration_s"] > 0).all()
        assert df.iloc[0]["duration_s"] == 15 * 60

    def test_missing_columns_raises_error(self):
        csv_content = b"""id;value;startDate
1;HKCategoryValueSleepAnalysisAsleepCore;2025-07-23"""

        buf = BytesIO(csv_content)
        with pytest.raises(CSVSchemaError):
            parse_sleep(buf)

    def test_unknown_stages_mapped_to_other(self):
        csv_content = b"""id;value;startDate;endDate
1;HKCategoryValueSleepAnalysisAsleepCore;2025-07-23 22:00:00 +0100;2025-07-23 23:00:00 +0100
2;UnknownStageValue;2025-07-23 23:00:00 +0100;2025-07-24 00:00:00 +0100"""

        buf = BytesIO(csv_content)
        df, report = parse_sleep(buf)

        assert df.iloc[1]["stage"] == "Other"
        assert report.unknown_stage_count == 1

    def test_invalid_time_range_dropped(self):
        csv_content = b"""id;value;startDate;endDate
1;HKCategoryValueSleepAnalysisAsleepCore;2025-07-23 22:00:00 +0100;2025-07-23 23:00:00 +0100
2;HKCategoryValueSleepAnalysisAsleepCore;2025-07-23 23:00:00 +0100;2025-07-23 22:00:00 +0100
3;HKCategoryValueSleepAnalysisAsleepDeep;2025-07-24 00:00:00 +0100;2025-07-24 01:00:00 +0100"""

        buf = BytesIO(csv_content)
        df, report = parse_sleep(buf)

        assert len(df) == 2
        assert report.rows_dropped_invalid == 1