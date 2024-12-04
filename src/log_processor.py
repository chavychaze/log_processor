import os
import argparse
from src.log_reader import LogFileReader
from src.db_writer import DatabaseWriter

def main():
    parser = argparse.ArgumentParser(description='Log Processing Tool')
    parser.add_argument('--file', required=True, help='Path to log file')
    parser.add_argument('--output', default='/output/filtered_logs.csv', 
                        help='Output CSV file path')
    parser.add_argument('--type', help='Filter by log type')
    parser.add_argument('--start-date', help='Start date for filtering')
    parser.add_argument('--end-date', help='End date for filtering')
    parser.add_argument('--keywords', nargs='+', help='Keywords to filter')
    parser.add_argument('--db-write', action='store_true', 
                        help='Write results to PostgreSQL')
    
    parser.add_argument('--pg-host', default='postgres', help='PostgreSQL host')
    parser.add_argument('--pg-port', default=5432, type=int, help='PostgreSQL port')
    parser.add_argument('--pg-db', default='logdb', help='PostgreSQL database')
    parser.add_argument('--pg-user', default='loguser', help='PostgreSQL username')
    parser.add_argument('--pg-password', default='logpassword', help='PostgreSQL password')
    
    args = parser.parse_args()

    log_reader = LogFileReader(args.file)
    
    filtered_logs = log_reader.filter_logs(
        log_type=args.type,
        start_date=args.start_date,
        end_date=args.end_date,
        keywords=args.keywords
    )

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    filtered_logs.to_csv(args.output, index=False)
    print(f"Filtered logs exported to {args.output}")

    if args.db_write:
        db_writer = DatabaseWriter(
            args.pg_host, args.pg_port, args.pg_db, 
            args.pg_user, args.pg_password
        )
        db_writer.write_logs(filtered_logs)
        print("Logs written to PostgreSQL")

if __name__ == "__main__":
    main()