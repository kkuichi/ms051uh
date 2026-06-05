import os
from datetime import timedelta

# Timezone
LOCAL_TZ: str = os.getenv("HD_LOCAL_TZ", "Europe/Bratislava")

# Stage mapping
STAGE_MAP: dict[str, str] = {
    "HKCategoryValueSleepAnalysisAsleepCore": "Core",
    "HKCategoryValueSleepAnalysisAsleepDeep": "Deep",
    "HKCategoryValueSleepAnalysisAsleepREM": "REM",
    "HKCategoryValueSleepAnalysisAsleepUnspecified": "Core",
    "HKCategoryValueSleepAnalysisAwake": "Awake",
    "HKCategoryValueSleepAnalysisInBed": "InBed",
}

ASLEEP_STAGES: frozenset[str] = frozenset({"Core", "Deep", "REM"})
KNOWN_STAGES: frozenset[str] = frozenset(STAGE_MAP.values())

# Validation
HR_VALID_RANGE: tuple[float, float] = (0.0, 240.0)

# Dipping
DIPPING_BASELINE_WINDOW: timedelta = timedelta(minutes=30)
DIPPING_MIN_BASELINE_SAMPLES: int = 3
DIPPING_HEALTHY_THRESHOLD_PCT: float = 10.0
DIPPING_REDUCED_THRESHOLD_PCT: float = 0.0

# Rolling / stress flag
ROLLING_7D_NIGHTS: int = 7
ROLLING_30D_NIGHTS: int = 30
STRESS_DELTA_BPM: float = 3.0
STRESS_MIN_CONSECUTIVE_NIGHTS: int = 2

# Tiered gates (FR-036)
MIN_NIGHTS_BASIC_KPIS: int = 1
MIN_NIGHTS_STAGE_STATS: int = 3
MIN_NIGHTS_7D_ROLLING: int = 7
MIN_NIGHTS_30D_ROLLING: int = 30

# OOM guard
OOM_HR_ROW_LIMIT: int = 500_000
OOM_MIN_USABLE_ROWS: int = 1_000

# Resampling
RESAMPLE_FREQ: str = "1min"
RESAMPLE_FFILL_LIMIT: int = 5

# Cache settings
CACHE_MAX_ENTRIES: int = 2
CACHE_TTL_SECONDS: int = 3600