"""Log file reader with memory-efficient processing and filtering capabilities."""
import mmap
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Any, Dict, Generator, List, Optional

import pandas as pd

from src.config import settings
from src.logger import logger


class LogFileReader:
    """Memory-efficient log file reader with filtering capabilities."""

    def __init__(self, log_file_path: str):
        self.log_file_path = log_file_path
        self.date_formats = [
            "%Y-%m-%d %H:%M:%S",
            "%d-%m-%Y %H:%M:%S",
            "%Y/%m/%d %H:%M:%S",
            "%m/%d/%Y %H:%M:%S",
            "%d/%m/%Y %H:%M:%S",
            "%Y-%m-%d",
            "%d-%m-%Y",
            "%Y/%m/%d",
            "%m/%d/%Y",
            "%d/%m/%Y",
        ]
        self._line_pattern = re.compile(r"\s*\|\s*")

    def parse_date(self, date_str: str) -> datetime:
        """Parse date string in various formats."""
        for fmt in self.date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        raise ValueError(f"Unable to parse date: {date_str}")

    def _process_line(
        self, line: str, filters: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Process a single log line and apply filters."""
        try:
            parts = self._line_pattern.split(line.strip(), maxsplit=2)
            if len(parts) < 3:
                return None

            timestamp_str, log_type_str, message = parts
            log_timestamp = self.parse_date(timestamp_str)

            # Apply filters
            if (
                filters.get("log_type")
                and filters["log_type"].lower() != log_type_str.lower()
            ):
                return None

            if filters.get("start_date"):
                start_dt = self.parse_date(filters["start_date"])
                if log_timestamp < start_dt:
                    return None

            if filters.get("end_date"):
                end_dt = self.parse_date(filters["end_date"])
                if log_timestamp > end_dt:
                    return None

            if filters.get("keywords"):
                if not all(kw.lower() in message.lower() for kw in filters["keywords"]):
                    return None

            return {
                "timestamp": log_timestamp,
                "type": log_type_str,
                "message": message,
            }
        except Exception as e:
            logger.error("Error processing line: %s, Error: %s", line, str(e))
            return None

    def _process_chunk(
        self, chunk: str, filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Make chunks for reeading purpose."""
        results = []
        for line in chunk.splitlines():
            processed = self._process_line(line, filters)
            if processed:
                results.append(processed)
        return results

    def filter_logs_generator(
        self,
        log_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        keywords: Optional[List[str]] = None,
    ) -> Generator[Dict[str, Any], None, None]:
        """Generate filtered log entries."""
        filters = {
            "log_type": log_type,
            "start_date": start_date,
            "end_date": end_date,
            "keywords": keywords,
        }

        with open(self.log_file_path, "rb") as f:
            with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                with ThreadPoolExecutor(max_workers=settings.MAX_WORKERS) as executor:
                    chunk_starts = range(0, len(mm), settings.CHUNK_SIZE)
                    futures = []

                    for start in chunk_starts:
                        end = min(start + settings.CHUNK_SIZE, len(mm))
                        chunk = mm[start:end].decode("utf-8", errors="ignore")
                        futures.append(
                            executor.submit(self._process_chunk, chunk, filters)
                        )

                    for future in futures:
                        yield from future.result()

    def filter_logs(
        self,
        log_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        keywords: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """Filter logs according to specified criteria and return as DataFrame."""
        import pandas as pd

        return pd.DataFrame(
            list(
                self.filter_logs_generator(
                    log_type=log_type,
                    start_date=start_date,
                    end_date=end_date,
                    keywords=keywords,
                )
            )
        )
