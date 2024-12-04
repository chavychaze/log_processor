from datetime import datetime

import pandas as pd
import pytest

from src.config import settings
from src.log_reader import LogFileReader


@pytest.fixture
def reader(sample_log_file):
    return LogFileReader(sample_log_file)


def test_parse_date_formats(reader):
    test_dates = [
        "2023-12-01 14:30:45",
        "01-12-2023 14:30:45",
        "2023/12/01 14:30:45",
        "12/01/2023 14:30:45",
        "2023-12-01",
    ]

    for date_str in test_dates:
        parsed_date = reader.parse_date(date_str)
        assert isinstance(parsed_date, datetime)
        assert parsed_date.year == 2023


def test_parse_date_invalid(reader):
    with pytest.raises(ValueError, match="Unable to parse date"):
        reader.parse_date("invalid-date-format")


def test_filter_logs_by_type(reader):
    filtered_df = reader.filter_logs(log_type="error")
    assert isinstance(filtered_df, pd.DataFrame)
    assert len(filtered_df) == 2
    assert all(row["type"] == "error" for _, row in filtered_df.iterrows())


def test_filter_logs_by_date_range(reader):
    filtered_df = reader.filter_logs(
        start_date="2023-12-01", end_date="2023-12-01 23:59:59"
    )
    assert len(filtered_df) == 5
    assert all(
        pd.Timestamp("2023-12-01") <= row["timestamp"] <= pd.Timestamp("2023-12-02")
        for _, row in filtered_df.iterrows()
    )


def test_filter_logs_by_keywords(reader):
    filtered_df = reader.filter_logs(keywords=["critical"])
    assert len(filtered_df) == 2
    assert all(
        "critical" in row["message"].lower() for _, row in filtered_df.iterrows()
    )


def test_filter_logs_combined(reader):
    filtered_df = reader.filter_logs(
        log_type="error", start_date="2023-12-01", keywords=["system", "failure"]
    )
    assert len(filtered_df) == 1
    assert "system failure" in filtered_df.iloc[0]["message"].lower()


def test_memory_efficiency(reader):
    gen = reader.filter_logs_generator()
    first_log = next(gen)
    assert isinstance(first_log, dict)
    assert all(key in first_log for key in ["timestamp", "type", "message"])


def test_parallel_processing(reader, monkeypatch):
    monkeypatch.setattr(settings, "MAX_WORKERS", 2)
    filtered_df = reader.filter_logs(log_type="error")
    assert len(filtered_df) == 2
