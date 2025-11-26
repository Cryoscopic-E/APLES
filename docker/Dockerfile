FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    git \
    openjdk-17-jdk \
    openjdk-17-jre \
    python-is-python3 \
    && rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH="$JAVA_HOME/bin:${PATH}"

WORKDIR /aples

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN rm requirements.txt