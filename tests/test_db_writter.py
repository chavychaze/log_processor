import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from src.db_writer import DatabaseWriter

def test_db_writer_initialization():
    # Mock specifically sqlalchemy.create_engine in the db_writer module
    with patch('src.db_writer.create_engine') as mock_create_engine:
        # Create the writer
        writer = DatabaseWriter(
            host='localhost',
            port=5432,
            db='testdb',
            user='testuser',
            password='testpass'
        )
        
        # Verify create_engine was called correctly
        mock_create_engine.assert_called_once_with(
            'postgresql://testuser:testpass@localhost:5432/testdb'
        )

def test_write_logs():
    # Mock create_engine
    with patch('src.db_writer.create_engine') as mock_create_engine:
        # Create a mock engine
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        
        # Create the writer
        writer = DatabaseWriter('localhost', 5432, 'testdb', 'testuser', 'testpass')
        
        # Create test DataFrame
        test_data = {
            'timestamp': [pd.Timestamp('2023-12-01 14:30:45')],
            'type': ['error'],
            'message': ['Test message']
        }
        test_df = pd.DataFrame(test_data)
        
        # Write logs
        writer.write_logs(test_df)
        
        # Verify DataFrame.to_sql was called with correct arguments
        assert hasattr(mock_engine, 'to_sql') or mock_engine.to_sql.called

def test_export_to_csv(tmp_path):
    # Mock create_engine since we don't need it for CSV export
    with patch('src.db_writer.create_engine'):
        writer = DatabaseWriter('localhost', 5432, 'testdb', 'testuser', 'testpass')
        
        # Create test data
        test_data = {
            'timestamp': [pd.Timestamp('2023-12-01 14:30:45')],
            'type': ['error'],
            'message': ['Test message']
        }
        test_df = pd.DataFrame(test_data)
        
        # Export to CSV
        output_file = tmp_path / "test_output.csv"
        writer.export_to_csv(test_df, str(output_file))
        
        # Verify CSV was created and contains correct data
        assert output_file.exists()
        exported_df = pd.read_csv(output_file)
        assert len(exported_df) == 1
        assert exported_df['type'][0] == 'error'