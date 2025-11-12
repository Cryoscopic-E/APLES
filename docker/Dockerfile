FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    git \
    openjdk-11-jre-headless \
    python-is-python3 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /aples

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN rm requirements.txt