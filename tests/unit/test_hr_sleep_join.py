import pandas as pd
import pytest
from health_dashboard import AlignmentError
from health_dashboard.alignment.hr_sleep_join import align_hr_to_stages


class TestHRSleepAlignment:

    def test_hr_within_sleep_interval(self):
        hr = pd.DataFrame({
            "ts_utc": pd.to_datetime([
                "2025-07-23 23:30:00+0100",
                "2025-07-24 00:00:00+0100",
                "2025-07-24 00:30:00+0100",
            ]),
            "ts_local": pd.to_datetime([
                "2025-07-23 23:30:00",
                "2025-07-24 00:00:00",
                "2025-07-24 00:30:00",
            ]).tz_localize("Europe/Bratislava"),
            "value": [65.0, 62.0, 61.0],
        })

        sleep = pd.DataFrame({
            "start_utc": pd.to_datetime(["2025-07-23 23:00:00+0100"]),
            "end_utc": pd.to_datetime(["2025-07-24 01:00:00+0100"]),
            "stage": ["Deep"],
        })

        result = align_hr_to_stages(hr, sleep)

        assert (result["stage"] == "Deep").all()

    def test_hr_outside_sleep_interval_marked_wake(self):
        hr = pd.DataFrame({
            "ts_utc": pd.to_datetime([
                "2025-07-23 21:00:00+0100",
                "2025-07-24 02:00:00+0100",
            ]),
            "ts_local": pd.to_datetime([
                "2025-07-23 21:00:00",
                "2025-07-24 02:00:00",
            ]).tz_localize("Europe/Bratislava"),
            "value": [75.0, 70.0],
        })

        sleep = pd.DataFrame({
            "start_utc": pd.to_datetime(["2025-07-23 23:00:00+0100"]),
            "end_utc": pd.to_datetime(["2025-07-24 01:00:00+0100"]),
            "stage": ["Deep"],
        })

        result = align_hr_to_stages(hr, sleep)

        assert (result["stage"] == "Wake/Out-of-sleep").all()

    def test_no_hr_samples_dropped(self):
        hr = pd.DataFrame({
            "ts_utc": pd.to_datetime([
                "2025-07-23 21:00:00+0100",
                "2025-07-23 23:00:00+0100",
                "2025-07-24 00:00:00+0100",
                "2025-07-24 02:00:00+0100",
            ]),
            "ts_local": pd.to_datetime([
                "2025-07-23 21:00:00",
                "2025-07-23 23:00:00",
                "2025-07-24 00:00:00",
                "2025-07-24 02:00:00",
            ]).tz_localize("Europe/Bratislava"),
            "value": [75.0, 68.0, 62.0, 70.0],
        })

        sleep = pd.DataFrame({
            "start_utc": pd.to_datetime(["2025-07-23 23:00:00+0100"]),
            "end_utc": pd.to_datetime(["2025-07-24 01:00:00+0100"]),
            "stage": ["Deep"],
        })

        result = align_hr_to_stages(hr, sleep)

        assert len(result) == len(hr)

    def test_unsorted_hr_raises_error(self):
        hr = pd.DataFrame({
            "ts_utc": pd.to_datetime([
                "2025-07-24 00:00:00+0100",
                "2025-07-23 23:00:00+0100",
            ]),
            "ts_local": pd.to_datetime([
                "2025-07-24 00:00:00",
                "2025-07-23 23:00:00",
            ]).tz_localize("Europe/Bratislava"),
            "value": [62.0, 68.0],
        })

        sleep = pd.DataFrame({
            "start_utc": pd.to_datetime(["2025-07-23 23:00:00+0100"]),
            "end_utc": pd.to_datetime(["2025-07-24 01:00:00+0100"]),
            "stage": ["Deep"],
        })

        with pytest.raises(AlignmentError, match="sorted"):
            align_hr_to_stages(hr, sleep)

    def test_unsorted_sleep_raises_error(self):
        """Unsorted sleep data should raise AlignmentError."""
        hr = pd.DataFrame({
            "ts_utc": pd.to_datetime(["2025-07-23 23:00:00+0100"]),
            "ts_local": pd.to_datetime(["2025-07-23 23:00:00"]).tz_localize("Europe/Bratislava"),
            "value": [68.0],
        })

        sleep = pd.DataFrame({
            "start_utc": pd.to_datetime([
                "2025-07-24 00:00:00+0100",
                "2025-07-23 23:00:00+0100",
            ]),
            "end_utc": pd.to_datetime([
                "2025-07-24 01:00:00+0100",
                "2025-07-23 23:30:00+0100",
            ]),
            "stage": ["Deep", "Core"],
        })

        with pytest.raises(AlignmentError, match="sorted"):
            align_hr_to_stages(hr, sleep)

    def test_night_date_added(self):
        """Result should contain night_date column."""
        hr = pd.DataFrame({
            "ts_utc": pd.to_datetime(["2025-07-23 23:30:00+0100"]),
            "ts_local": pd.to_datetime(["2025-07-23 23:30:00"]).tz_localize("Europe/Bratislava"),
            "value": [65.0],
        })

        sleep = pd.DataFrame({
            "start_utc": pd.to_datetime(["2025-07-23 23:00:00+0100"]),
            "end_utc": pd.to_datetime(["2025-07-24 01:00:00+0100"]),
            "stage": ["Deep"],
        })

        result = align_hr_to_stages(hr, sleep)

        assert "night_date" in result.columns