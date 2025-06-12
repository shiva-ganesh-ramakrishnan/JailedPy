FROM python:3.11-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir flask pandas numpy

CMD ["python3", "app.py"]

