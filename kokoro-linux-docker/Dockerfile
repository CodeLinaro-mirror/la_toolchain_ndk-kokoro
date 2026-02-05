FROM ubuntu:24.04

# Install dependencies
RUN apt-get update \
 && apt-get install -y --no-install-recommends docker-cli \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*
