import os
import tempfile

import pytest


@pytest.fixture
def sample_log_file():
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write("2023-12-01 14:30:45 | error | Critical system failure\n")
        f.write("2023/12/01 15:45:30 | warning | System warning message\n")
        f.write("01-12-2023 16:20:15 | info | Normal operation\n")
        f.write("12/01/2023 17:10:00 | error | Another critical error\n")
        f.write("2023-12-01 | debug | Debug message\n")

    yield f.name
    os.unlink(f.name)


@pytest.fixture
def large_sample_log():
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        for i in range(1000):
            f.write(f"2023-12-01 14:30:{i%60} | error | Test message {i}\n")

    yield f.name
    os.unlink(f.name)
