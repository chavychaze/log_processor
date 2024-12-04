"""Main log processing module."""
import argparse
import os

from src.db_writer import DatabaseWriter, DBConfig
from src.log_reader import LogFileReader
from src.logger import logger


def main() -> None:
    """Process logs according to command line arguments."""
    parser = argparse.ArgumentParser(description="Log Processing Tool")
    parser.add_argument("--file", required=True, help="Path to log file")
    parser.add_argument(
        "--output", default="/output/filtered_logs.csv", help="Output CSV file path"
    )
    parser.add_argument("--type", help="Filter by log type")
    parser.add_argument("--start-date", help="Start date for filtering")
    parser.add_argument("--end-date", help="End date for filtering")
    parser.add_argument("--keywords", nargs="+", help="Keywords to filter")
    parser.add_argument(
        "--db-write", action="store_true", help="Write results to PostgreSQL"
    )

    args = parser.parse_args()

    log_reader = LogFileReader(args.file)
    filtered_logs = log_reader.filter_logs(
        log_type=args.type,
        start_date=args.start_date,
        end_date=args.end_date,
        keywords=args.keywords,
    )

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    filtered_logs.to_csv(args.output, index=False)
    logger.info("Filtered logs exported to %s", args.output)

    if args.db_write:
        db_config = DBConfig(
            host="localhost",
            port=5432,
            db="testdb",
            user="testuser",
            password="testpass",
        )
        writer = DatabaseWriter(db_config)
        writer.write_logs(filtered_logs)
        logger.info("Logs written to PostgreSQL")


if __name__ == "__main__":
    main()
