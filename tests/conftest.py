"""Pytest configuration and fixtures."""
import pytest
from pathlib import Path
from io import BytesIO
import pandas as pd


@pytest.fixture
def fixtures_dir() -> Path:
    """Return path to test fixtures directory."""
    return Path(__file__).parent / "data"


@pytest.fixture
def heart_rate_sample_csv(fixtures_dir: Path) -> BytesIO:
    """Load heart rate sample CSV as BytesIO buffer."""
    path = fixtures_dir / "heart_rate_sample.csv"
    content = path.read_bytes()
    buf = BytesIO(content)
    buf.seek(0)
    return buf


@pytest.fixture
def sleep_sample_csv(fixtures_dir: Path) -> BytesIO:
    """Load sleep sample CSV as BytesIO buffer."""
    path = fixtures_dir / "sleep_sample.csv"
    content = path.read_bytes()
    buf = BytesIO(content)
    buf.seek(0)
    return buf


@pytest.fixture
def synthetic_large_csv(fixtures_dir: Path) -> BytesIO:
    """Load large synthetic HR CSV (for OOM testing) as BytesIO buffer."""
    path = fixtures_dir / "synthetic_large.csv"
    content = path.read_bytes()
    buf = BytesIO(content)
    buf.seek(0)
    return buf


@pytest.fixture
def synthetic_stress_hr_csv(fixtures_dir: Path) -> BytesIO:
    """Load synthetic HR CSV for stress flag testing as BytesIO buffer."""
    path = fixtures_dir / "synthetic_stress_hr.csv"
    content = path.read_bytes()
    buf = BytesIO(content)
    buf.seek(0)
    return buf


@pytest.fixture
def synthetic_stress_sleep_csv(fixtures_dir: Path) -> BytesIO:
    """Load synthetic sleep CSV for stress flag testing as BytesIO buffer."""
    path = fixtures_dir / "synthetic_stress_sleep.csv"
    content = path.read_bytes()
    buf = BytesIO(content)
    buf.seek(0)
    return buf