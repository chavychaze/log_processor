"""Database writer for log processing with connection pooling."""
from dataclasses import dataclass

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.pool import QueuePool

from src.config import settings
from src.logger import logger


@dataclass
class DBConfig:
    """Database configuration."""

    host: str
    port: int
    db: str
    user: str
    password: str

    # pylint: disable=consider-using-f-string
    @property
    def connection_string(self) -> str:
        """Get database connection string."""
        return "postgresql://%s:%s@%s:%s/%s" % (
            self.user,
            self.password,
            self.host,
            self.port,
            self.db,
        )

    # pylint: enable=consider-using-f-string


class DatabaseWriter:
    """Handles database operations for log processing."""

    def __init__(self, config: DBConfig) -> None:
        """Initialize database connection with pooling."""
        self.config = config
        self.engine = self._create_engine()

    def _create_engine(self) -> Engine:
        """Create SQLAlchemy engine with connection pooling."""
        return create_engine(
            self.config.connection_string,
            poolclass=QueuePool,
            pool_size=settings.DB_POOL_SIZE,
            max_overflow=settings.DB_MAX_OVERFLOW,
            pool_timeout=30,
            pool_pre_ping=True,
        )

    def write_logs(self, logs_df: pd.DataFrame, table_name: str = "logs") -> None:
        """Write logs to database."""
        try:
            logs_df.to_sql(
                table_name,
                self.engine,
                if_exists="append",
                index=False,
                method="multi",
                chunksize=settings.DB_CHUNK_SIZE,
            )
            logger.info("Successfully wrote %s records to database", len(logs_df))
        except Exception as e:
            logger.error("Database write error: %s", str(e))
            raise

    def export_to_csv(self, logs_df: pd.DataFrame, output_path: str) -> None:
        """Write logs to csv file."""
        try:
            logs_df.to_csv(output_path, index=False)
            logger.info("Successfully exported logs to %s", output_path)
        except Exception as e:
            logger.error("CSV export error: %s", str(e))
            raise

    def cleanup(self) -> None:
        """Clean up database connections."""
        try:
            self.engine.dispose()
            logger.info("Database connections disposed")
        except Exception as e:
            logger.error("Error during cleanup: %s", str(e))
