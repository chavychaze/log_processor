import pytest
import os
import tempfile

@pytest.fixture
def sample_log_file():
    """Create a temporary log file with sample data."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write("2023-12-01 14:30:45 | error | Critical system failure\n")
        f.write("2023/12/01 15:45:30 | warning | System warning message\n")
        f.write("01-12-2023 16:20:15 | info | Normal operation\n")
        f.write("12/01/2023 17:10:00 | error | Another critical error\n")
        f.write("2023-12-01 | debug | Debug message\n")
    
    yield f.name
    os.unlink(f.name)

@pytest.fixture
def mock_db_connection(mocker):
    """Mock SQLAlchemy engine and connection."""
    mock_engine = mocker.patch('sqlalchemy.create_engine')
    mock_connection = mocker.MagicMock()
    mock_engine.return_value = mock_connection
    return mock_engine, mock_connection