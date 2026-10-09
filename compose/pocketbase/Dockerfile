FROM alpine:3.23.3
ARG PB_VERSION=0.40.4
ARG PB_SHA256=9042ec818570e79c3628dadcd0a756c1496d9e1173918ec409d133c02f82e5fa
RUN apk add --no-cache ca-certificates unzip wget && \
    wget -q "https://github.com/pocketbase/pocketbase/releases/download/v${PB_VERSION}/pocketbase_${PB_VERSION}_linux_amd64.zip" -O /tmp/pb.zip && \
    echo "${PB_SHA256}  /tmp/pb.zip" | sha256sum -c - && \
    unzip /tmp/pb.zip pocketbase -d /usr/local/bin && rm /tmp/pb.zip
USER 1000:1000
WORKDIR /pb
ENTRYPOINT ["pocketbase"]
CMD ["serve", "--http=0.0.0.0:8090", "--dir=/pb/pb_data"]
