import pandas as pd
from datetime import date
from health_dashboard.alignment.resampling import resample_hr_1min


class TestResamplingToOneMinute:
    def test_resample_to_1min_bins(self):
        hr = pd.DataFrame({
            "ts_utc": pd.to_datetime([
                "2025-07-23 23:00:00+0100",
                "2025-07-23 23:00:30+0100",
                "2025-07-23 23:01:00+0100",
                "2025-07-23 23:01:30+0100",
            ]),
            "ts_local": pd.to_datetime([
                "2025-07-23 23:00:00",
                "2025-07-23 23:00:30",
                "2025-07-23 23:01:00",
                "2025-07-23 23:01:30",
            ]).tz_localize("Europe/Bratislava"),
            "value": [65.0, 66.0, 64.0, 65.0],
            "stage": ["Deep", "Deep", "Deep", "Deep"],
            "night_date": [date(2025, 7, 24)] * 4,
        })

        result = resample_hr_1min(hr)

        assert len(result) >= 2

    def test_mean_hr_computed(self):
        hr = pd.DataFrame({
            "ts_utc": pd.to_datetime([
                "2025-07-23 23:00:00+0100",
                "2025-07-23 23:00:30+0100",
                "2025-07-23 23:01:00+0100",
            ]),
            "ts_local": pd.to_datetime([
                "2025-07-23 23:00:00",
                "2025-07-23 23:00:30",
                "2025-07-23 23:01:00",
            ]).tz_localize("Europe/Bratislava"),
            "value": [60.0, 70.0, 65.0],
            "stage": ["Deep"] * 3,
            "night_date": [date(2025, 7, 24)] * 3,
        })

        result = resample_hr_1min(hr)

        assert result["hr_mean"].iloc[0] == 65.0

    def test_forward_fill_capped(self):
        hr = pd.DataFrame({
            "ts_utc": pd.to_datetime([
                "2025-07-23 23:00:00+0100",
                "2025-07-23 23:10:00+0100",
            ]),
            "ts_local": pd.to_datetime([
                "2025-07-23 23:00:00",
                "2025-07-23 23:10:00",
            ]).tz_localize("Europe/Bratislava"),
            "value": [65.0, 60.0],
            "stage": ["Deep", "Deep"],
            "night_date": [date(2025, 7, 24)] * 2,
        })

        result = resample_hr_1min(hr, max_ffill_minutes=5)

        assert result.iloc[0]["hr_mean"] == 65.0
        assert result.iloc[1]["hr_mean"] == 65.0
        assert result.iloc[5]["hr_mean"] == 65.0
        assert pd.isna(result.iloc[6]["hr_mean"])
        assert result.iloc[10]["hr_mean"] == 60.0

    def test_column_structure(self):
        hr = pd.DataFrame({
            "ts_utc": pd.to_datetime(["2025-07-23 23:00:00+0100"]),
            "ts_local": pd.to_datetime(
                ["2025-07-23 23:00:00"]
            ).tz_localize("Europe/Bratislava"),
            "value": [65.0],
            "stage": ["Deep"],
            "night_date": [date(2025, 7, 24)],
        })

        result = resample_hr_1min(hr)

        assert "ts_utc" in result.columns
        assert "hr_mean" in result.columns