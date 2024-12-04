import os
import timeit

import memory_profiler

from src.log_reader import LogFileReader


def create_large_log(size_mb=100):
    """Create test log file of specified size in MB."""
    file_path = "test_large.log"
    line_size = 100  # approximate bytes per line
    lines_needed = (size_mb * 1024 * 1024) // line_size

    with open(file_path, "w") as f:
        for i in range(lines_needed):
            f.write(
                f"2023-12-01 14:30:{i%60} | {'error' if i%3==0 else 'info'} | Test message {i} with some additional content\n"
            )
    return file_path


def benchmark_memory():
    """Measure memory usage during processing."""
    file_path = create_large_log()

    @memory_profiler.profile
    def process_file():
        reader = LogFileReader(file_path)
        logs = reader.filter_logs(log_type="error")
        return len(logs)

    process_file()
    os.remove(file_path)


def benchmark_processing_speed():
    """Measure processing speed for different file sizes."""
    sizes = [10, 50, 100]  # MB
    results = {}

    for size in sizes:
        file_path = create_large_log(size)
        reader = LogFileReader(file_path)

        def test_full_processing():
            logs = reader.filter_logs(
                log_type="error", start_date="2023-12-01", keywords=["Test"]
            )
            return len(logs)

        time = timeit.timeit(test_full_processing, number=3)
        results[size] = time / 3  # average time
        os.remove(file_path)

    return results


def benchmark_chunk_sizes():
    """Compare performance with different chunk sizes."""
    file_path = create_large_log(50)
    chunk_sizes = [1024 * 1024, 5 * 1024 * 1024, 10 * 1024 * 1024]
    results = {}

    for chunk_size in chunk_sizes:
        reader = LogFileReader(file_path)
        reader.CHUNK_SIZE = chunk_size

        time = timeit.timeit(
            lambda: len(reader.filter_logs(log_type="error")), number=3
        )
        results[chunk_size // 1024 // 1024] = time / 3

    os.remove(file_path)
    return results


if __name__ == "__main__":
    print("\nMemory Profile:")
    benchmark_memory()

    print("\nProcessing Speed (seconds):")
    speed_results = benchmark_processing_speed()
    for size, time in speed_results.items():
        print(f"{size}MB: {time:.2f}s")

    print("\nChunk Size Impact (seconds):")
    chunk_results = benchmark_chunk_sizes()
    for size, time in chunk_results.items():
        print(f"{size}MB chunks: {time:.2f}s")
