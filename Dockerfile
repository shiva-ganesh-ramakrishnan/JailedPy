FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    git build-essential flex bison \
    clang make wget curl \
    ca-certificates pkg-config \
    libprotobuf-dev protobuf-compiler \
    libnl-3-dev libnl-genl-3-dev libnl-route-3-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/google/nsjail.git /tmp/nsjail && \
    cd /tmp/nsjail && make -j$(nproc) && cp nsjail /usr/local/bin/ && \
    rm -rf /tmp/nsjail

COPY . /app

RUN pip install --no-cache-dir flask pandas numpy

CMD ["python3", "app.py"]

