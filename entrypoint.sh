#!/bin/bash

# If arguments are provided, pass them to the Python script
if [ $# -gt 0 ]; then
    python -m src.log_processor "$@"
else
    # Default arguments if none provided
    python -m src.log_processor \
        --file /logs/logfile.log \
        --output /output/filtered_logs.csv \
        --db-write
fi