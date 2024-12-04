from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from src.db_writer import DatabaseWriter, DBConfig


@pytest.fixture
def db_config():
    return DBConfig(
        host="localhost", port=5432, db="testdb", user="testuser", password="testpass"
    )


@pytest.fixture
def mock_engine():
    with patch("src.db_writer.create_engine") as mock_create:
        engine = MagicMock()
        mock_create.return_value = engine
        yield mock_create, engine


@pytest.fixture
def sample_df():
    return pd.DataFrame(
        {
            "timestamp": [pd.Timestamp("2023-12-01 14:30:45")],
            "type": ["error"],
            "message": ["Test message"],
        }
    )


def test_db_writer_initialization(mock_engine, db_config):
    mock_create, _ = mock_engine
    writer = DatabaseWriter(db_config)
    mock_create.assert_called_once()


def test_write_logs(mock_engine, db_config, sample_df):
    _, engine = mock_engine
    writer = DatabaseWriter(db_config)
    writer.write_logs(sample_df)
    assert hasattr(sample_df, "to_sql")


def test_export_to_csv(mock_engine, db_config, sample_df, tmp_path):
    writer = DatabaseWriter(db_config)
    output_file = tmp_path / "test_output.csv"
    writer.export_to_csv(sample_df, str(output_file))
    assert output_file.exists()
    exported_df = pd.read_csv(output_file)
    assert len(exported_df) == 1
    assert exported_df["type"][0] == "error"


def test_cleanup(mock_engine, db_config):
    _, engine = mock_engine
    writer = DatabaseWriter(db_config)
    writer.cleanup()
    engine.dispose.assert_called_once()
