FROM us-docker.pkg.dev/artifact-foundry-prod/docker-3p-trusted/ubuntu:20.04

# Install dependencies
RUN apt-get update \
 && apt-get install -y --no-install-recommends docker.io \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*
