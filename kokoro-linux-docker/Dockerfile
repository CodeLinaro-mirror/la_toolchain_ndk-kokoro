FROM --platform=$BUILDPLATFORM us-central1-docker.pkg.dev/kokoro-container-bakery/kokoro/ubuntu/ubuntu2004/full:current

# Install dependencies
RUN apt-get update \
 && apt-get install -y --no-install-recommends docker-cli \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*
