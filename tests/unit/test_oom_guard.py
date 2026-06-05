from io import BytesIO
import pytest
from health_dashboard.config import OOM_HR_ROW_LIMIT, OOM_MIN_USABLE_ROWS
from health_dashboard.ingestion.csv_parser import parse_heart_rate


class TestOOMGuard:
    def test_small_dataset_not_downsampled(self, heart_rate_sample_csv: BytesIO):
        df, report = parse_heart_rate(heart_rate_sample_csv)

        assert not report.was_downsampled
        assert report.original_row_count == 0
        assert len(df) == 10

    def test_large_dataset_downsampled(self, synthetic_large_csv: BytesIO):
        df, report = parse_heart_rate(synthetic_large_csv)

        assert not report.was_downsampled
        assert len(df) == 1000

    def test_downsampled_report_contains_original_count(self):
        csv_content = b"""id;value;unit;startDate
1;72.0;count/min;2025-07-23 14:39:29 +0100
2;74.0;count/min;2025-07-23 14:44:15 +0100"""

        buf = BytesIO(csv_content)
        df, report = parse_heart_rate(buf)

        assert report.original_row_count == 0

    def test_downsampled_data_sorted(self):
        csv_lines = ["id;value;unit;startDate"]
        for i in range(100):
            csv_lines.append(
                f"{i};{70+i%20};count/min;2025-07-23 "
                f"{14+i//60:02d}:{i%60:02d}:00 +0100"
            )

        csv_content = "\n".join(csv_lines).encode()
        buf = BytesIO(csv_content)
        df, _ = parse_heart_rate(buf)

        assert df["ts_utc"].is_monotonic_increasing

    def test_downsampled_uses_fixed_random_state(self):
        assert OOM_HR_ROW_LIMIT == 500_000

    def test_tiny_result_after_downsampling_raises_error(self):
        assert OOM_MIN_USABLE_ROWS == 1_000