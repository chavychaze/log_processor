import pytest
from datetime import datetime
from src.log_reader import LogFileReader

def test_parse_date_formats(sample_log_file):
    reader = LogFileReader(sample_log_file)
    
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

def test_parse_date_invalid():
    reader = LogFileReader("dummy.log")
    with pytest.raises(ValueError):
        reader.parse_date("invalid-date-format")

def test_filter_logs(sample_log_file):
    reader = LogFileReader(sample_log_file)
    
    # Test filtering by type
    filtered_df = reader.filter_logs(log_type="error")
    assert len(filtered_df) == 2
    assert all(row['type'] == 'error' for _, row in filtered_df.iterrows())
    
    # Test filtering by date range
    filtered_df = reader.filter_logs(
        start_date="2023-12-01",
        end_date="2023-12-01 23:59:59"
    )
    assert len(filtered_df) == 5  # All logs are from same date
    
    # Test filtering by keywords
    filtered_df = reader.filter_logs(keywords=["critical"])
    assert len(filtered_df) == 2  # Both error messages contain 'critical'
    
    # Test combined filtering with specific error message
    filtered_df = reader.filter_logs(
        log_type="error",
        start_date="2023-12-01",
        keywords=["system", "failure"]  # More specific keywords
    )
    assert len(filtered_df) == 1

def test_memory_efficiency(sample_log_file):
    reader = LogFileReader(sample_log_file)
    
    generator = reader.filter_logs_generator()
    first_log = next(generator)
    assert isinstance(first_log, dict)
    assert 'timestamp' in first_log
    assert 'type' in first_log
    assert 'message' in first_log