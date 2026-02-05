FROM --platform=$BUILDPLATFORM us-central1-docker.pkg.dev/kokoro-container-bakery/kokoro/ubuntu/ubuntu2004/full:current

# Remove some package sources that we don't need that are having GPG issues.
# These can be removed once the base images have been updated.
rm -f /etc/apt/sources.list.d/yarn.list
rm -f /etc/apt/sources.list.d/nodesource.list

# Install dependencies
RUN apt-get update \
 && apt-get install -y --no-install-recommends docker-cli \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*
