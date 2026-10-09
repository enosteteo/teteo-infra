FROM alpine:3.23.3
ARG MC_VERSION=RELEASE.2025-08-13T08-35-41Z
ARG MC_SHA256=01f866e9c5f9b87c2b09116fa5d7c06695b106242d829a8bb32990c00312e891
RUN apk add --no-cache ca-certificates wget && \
    wget -q "https://github.com/minio/mc/releases/download/${MC_VERSION}/mc.linux-amd64.${MC_VERSION}" -O /usr/local/bin/mc && \
    echo "${MC_SHA256}  /usr/local/bin/mc" | sha256sum -c - && \
    chmod 755 /usr/local/bin/mc
ENTRYPOINT ["mc"]
