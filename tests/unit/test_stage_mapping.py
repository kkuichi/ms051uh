import pandas as pd
from health_dashboard.ingestion.stage_mapping import map_stages, is_asleep_stage


class TestMapStages:
    def test_known_stages_mapped(self):
        df = pd.DataFrame({
            "value": [
                "HKCategoryValueSleepAnalysisAsleepCore",
                "HKCategoryValueSleepAnalysisAsleepDeep",
                "HKCategoryValueSleepAnalysisAsleepREM",
                "HKCategoryValueSleepAnalysisAwake",
                "HKCategoryValueSleepAnalysisInBed",
            ]
        })

        result = map_stages(df)

        assert result["stage"].tolist() == ["Core", "Deep", "REM", "Awake", "InBed"]

    def test_unknown_stage_mapped_to_other(self):
        df = pd.DataFrame({"value": ["UnknownValue", "AnotherUnknown"]})

        result = map_stages(df)

        assert (result["stage"] == "Other").all()

    def test_legacy_asleep_unspecified_maps_to_core(self):
        df = pd.DataFrame({"value": ["HKCategoryValueSleepAnalysisAsleepUnspecified"]})

        result = map_stages(df)

        assert result["stage"].iloc[0] == "Core"

    def test_stage_is_categorical(self):
        df = pd.DataFrame({"value": ["HKCategoryValueSleepAnalysisAsleepCore"]})

        result = map_stages(df)

        assert result["stage"].dtype.name == "category"

    def test_custom_raw_column_name(self):
        df = pd.DataFrame({"raw_value": ["HKCategoryValueSleepAnalysisAsleepCore"]})

        result = map_stages(df, raw_col="raw_value")

        assert result["stage"].iloc[0] == "Core"


class TestIsAsleepStage:
    def test_asleep_stages_recognized(self):
        assert is_asleep_stage("Core")
        assert is_asleep_stage("Deep")
        assert is_asleep_stage("REM")

    def test_non_asleep_stages_not_recognized(self):
        assert not is_asleep_stage("Awake")
        assert not is_asleep_stage("InBed")
        assert not is_asleep_stage("Other")

    def test_unknown_stage_not_recognized(self):
        assert not is_asleep_stage("UnknownStage")