import pandas as pd
import pytest
from datetime import date
from health_dashboard.alignment.night_grouping import assign_night_date


class TestNightGrouping:
    def test_midnight_maps_to_same_date(self):
        tz_str = "Europe/Bratislava"
        ts = pd.to_datetime("2025-07-24 00:00:00", utc=True).tz_convert(tz_str)
        ts_series = pd.Series([ts])

        result = assign_night_date(ts_series)

        assert result.iloc[0] == date(2025, 7, 24)

    def test_noon_maps_to_next_date(self):
        tz_str = "Europe/Bratislava"
        ts = pd.to_datetime("2025-07-24 12:00:00", utc=True).tz_convert(tz_str)
        ts_series = pd.Series([ts])

        result = assign_night_date(ts_series)

        assert result.iloc[0] == date(2025, 7, 25)

    def test_evening_maps_to_next_date(self):
        tz_str = "Europe/Bratislava"
        ts = pd.to_datetime("2025-07-23 22:00:00", utc=True).tz_convert(tz_str)
        ts_series = pd.Series([ts])

        result = assign_night_date(ts_series)

        assert result.iloc[0] == date(2025, 7, 24)

    def test_early_morning_maps_to_same_date(self):
        tz_str = "Europe/Bratislava"
        ts = pd.to_datetime("2025-07-24 06:00:00", utc=True).tz_convert(tz_str)
        ts_series = pd.Series([ts])

        result = assign_night_date(ts_series)

        assert result.iloc[0] == date(2025, 7, 24)

    def test_non_aware_raises_error(self):
        ts_naive = pd.Series([pd.Timestamp("2025-07-24 12:00:00")])

        with pytest.raises(ValueError, match="timezone-aware"):
            assign_night_date(ts_naive)

    def test_entire_sleep_session_same_night_date(self):
        tz_str = "Europe/Bratislava"
        times = [
            "2025-07-23 22:00:00",
            "2025-07-23 23:00:00",
            "2025-07-24 00:00:00",
            "2025-07-24 06:00:00",
            "2025-07-24 08:00:00",
        ]
        ts_series = pd.Series([
            pd.to_datetime(t, utc=True).tz_convert(tz_str)
            for t in times
        ])

        result = assign_night_date(ts_series)

        assert (result == date(2025, 7, 24)).all()

    def test_single_night_boundary(self):
        tz_str = "Europe/Bratislava"
        ts_series = pd.Series([
            pd.to_datetime("2025-07-24 09:59:00", utc=True).tz_convert(tz_str),
            pd.to_datetime("2025-07-24 10:00:00", utc=True).tz_convert(tz_str),
            pd.to_datetime("2025-07-24 10:01:00", utc=True).tz_convert(tz_str),
        ])

        result = assign_night_date(ts_series)

        assert result.iloc[0] == date(2025, 7, 24)
        assert result.iloc[1] == date(2025, 7, 25)
        assert result.iloc[2] == date(2025, 7, 25)