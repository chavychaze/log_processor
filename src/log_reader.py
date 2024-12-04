import re
from datetime import datetime
import pandas as pd
from typing import List, Optional, Generator

class LogFileReader:
    def __init__(self, log_file_path: str):
        self.log_file_path = log_file_path
        self.date_formats = [
            '%Y-%m-%d %H:%M:%S',     # 2023-12-01 14:30:45
            '%d-%m-%Y %H:%M:%S',     # 01-12-2023 14:30:45
            '%Y/%m/%d %H:%M:%S',     # 2023/12/01 14:30:45
            '%m/%d/%Y %H:%M:%S',     # 12/01/2023 14:30:45
            '%d/%m/%Y %H:%M:%S',     # 01/12/2023 14:30:45
            '%Y-%m-%d',               # 2023-12-01
            '%d-%m-%Y',               # 01-12-2023
            '%Y/%m/%d',               # 2023/12/01
            '%m/%d/%Y',               # 12/01/2023
            '%d/%m/%Y'                # 01/12/2023
        ]

    def parse_date(self, date_str: str) -> datetime:
        for fmt in self.date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        raise ValueError(f"Unable to parse date: {date_str}")

    def filter_logs_generator(self, 
                    log_type: Optional[str] = None, 
                    start_date: Optional[str] = None, 
                    end_date: Optional[str] = None, 
                    keywords: Optional[List[str]] = None) -> Generator[dict, None, None]:
        start_dt = self.parse_date(start_date) if start_date else None
        end_dt = self.parse_date(end_date) if end_date else None

        with open(self.log_file_path, 'r', encoding='utf-8', errors='ignore', buffering=1024*1024) as file:
            for line in file:
                try:
                    parts = re.split(r'\s*\|\s*', line.strip(), maxsplit=2)
                    if len(parts) < 3:
                        continue
                    
                    timestamp_str, log_type_str, message = parts
                    
                    log_timestamp = self.parse_date(timestamp_str)
                    
                    type_match = not log_type or log_type.lower() == log_type_str.lower()
                    date_match = (not start_dt or log_timestamp >= start_dt) and \
                                 (not end_dt or log_timestamp <= end_dt)
                    keyword_match = not keywords or \
                        all(keyword.lower() in message.lower() for keyword in keywords)
                    
                    if type_match and date_match and keyword_match:
                        yield {
                            'timestamp': log_timestamp,
                            'type': log_type_str,
                            'message': message
                        }
                    
                except Exception as e:
                    print(f"Error parsing line: {line}")

    def filter_logs(self, **kwargs) -> pd.DataFrame:
        return pd.DataFrame(self.filter_logs_generator(**kwargs))