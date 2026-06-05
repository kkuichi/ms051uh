from io import BytesIO
from pathlib import Path
from health_dashboard.analytics.nightly_metrics import compute_nightly_metrics
from health_dashboard.ingestion.csv_parser import parse_heart_rate, parse_sleep


class TestEndToEnd:
    def test_full_pipeline_with_sample_data(self):
        fixtures_dir = Path("tests/data")

        hr_buf = BytesIO((fixtures_dir / "heart_rate_sample.csv").read_bytes())
        sleep_buf = BytesIO((fixtures_dir / "sleep_sample.csv").read_bytes())

        raw_hr, hr_report = parse_heart_rate(hr_buf, filename="sample_hr.csv")
        raw_sleep, sleep_report = parse_sleep(sleep_buf, filename="sample_sleep.csv")

        assert len(raw_hr) > 0
        assert len(raw_sleep) > 0
        assert not hr_report.was_downsampled

        nightly_df = compute_nightly_metrics(raw_hr, raw_sleep)

        assert len(nightly_df) > 0
        assert "night_date" in nightly_df.index.name or nightly_df.index.name == "night_date"

    def test_pipeline_metrics_completeness(self):
        fixtures_dir = Path("tests/data")

        hr_buf = BytesIO((fixtures_dir / "heart_rate_sample.csv").read_bytes())
        sleep_buf = BytesIO((fixtures_dir / "sleep_sample.csv").read_bytes())

        raw_hr, _ = parse_heart_rate(hr_buf)
        raw_sleep, _ = parse_sleep(sleep_buf)

        nightly_df = compute_nightly_metrics(raw_hr, raw_sleep)

        essential_cols = [
            "mean_core",
            "mean_deep",
            "mean_rem",
            "total_sleep_s",
            "baseline_pre_sleep_hr",
            "dip_pct",
            "dip_classification",
        ]

        for col in essential_cols:
            assert col in nightly_df.columns, f"Missing column: {col}"

    def test_pipeline_with_synthetic_stress_data(self):
        fixtures_dir = Path("tests/data")

        hr_buf = BytesIO((fixtures_dir / "synthetic_stress_hr.csv").read_bytes())
        sleep_buf = BytesIO((fixtures_dir / "synthetic_stress_sleep.csv").read_bytes())

        raw_hr, _ = parse_heart_rate(hr_buf)
        raw_sleep, _ = parse_sleep(sleep_buf)

        nightly_df = compute_nightly_metrics(raw_hr, raw_sleep)

        assert len(nightly_df) >= 10
        assert "roll_7d_deep_hr" in nightly_df.columns
        assert "stress_flag" in nightly_df.columns
        assert nightly_df["stress_flag"].dtype == bool
