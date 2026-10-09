FROM golang:1.24.8 AS builder
ARG MINIO_VERSION=RELEASE.2025-10-15T17-29-55Z
ENV CGO_ENABLED=0 GOMAXPROCS=2
RUN go install -p 2 github.com/minio/minio@${MINIO_VERSION}
FROM alpine:3.23.3
RUN apk add --no-cache ca-certificates curl
COPY --from=builder /go/bin/minio /usr/local/bin/minio
ENTRYPOINT ["minio"]
CMD ["server", "/data", "--console-address", ":9001"]
