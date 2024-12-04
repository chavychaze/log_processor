import timeit
from src.log_reader import LogFileReader
import tempfile


def create_sample_log(size=1000):
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        for i in range(size):
            f.write(f"2023-12-01 14:30:{i%60} | error | Test message {i}\n")
        return f.name


def benchmark_log_reading():
    file_path = create_sample_log()
    reader = LogFileReader(file_path)

    def read_test():
        return len(reader.filter_logs(log_type="error"))

    time = timeit.timeit(read_test, number=100)
    print(f"Log reading benchmark: {time:.2f} seconds")


def benchmark_filtering():
    file_path = create_sample_log()
    reader = LogFileReader(file_path)

    def filter_test():
        return len(reader.filter_logs(start_date="2023-12-01", keywords=["Test"]))

    time = timeit.timeit(filter_test, number=100)
    print(f"Filtering benchmark: {time:.2f} seconds")


if __name__ == "__main__":
    benchmark_log_reading()
    benchmark_filtering()
