FROM python:3.9-slim

WORKDIR /app

ENV PYTHONPATH=/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY entrypoint.sh .
COPY benchmarks/ ./benchmarks/

RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
