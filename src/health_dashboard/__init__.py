from dataclasses import dataclass


class HealthDashboardError(Exception):
    pass


class CSVSchemaError(HealthDashboardError):
    pass


class AlignmentError(HealthDashboardError):
    pass


class OOMGuardError(HealthDashboardError):
    pass


@dataclass(frozen=True)
class IngestionReport:
    filename: str
    rows_read: int
    rows_dropped_invalid: int
    rows_dropped_out_of_range: int
    unknown_stage_count: int
    was_downsampled: bool
    original_row_count: int


__all__ = [
    "HealthDashboardError",
    "CSVSchemaError",
    "AlignmentError",
    "OOMGuardError",
    "IngestionReport",
]