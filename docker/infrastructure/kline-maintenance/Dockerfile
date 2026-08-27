FROM curlimages/curl:8.16.0@sha256:463eaf6072688fe96ac64fa623fe73e1dbe25d8ad6c34404a669ad3ce1f104b6 AS certificates

FROM scratch

COPY kline-continuity-audit /kline-continuity-audit
COPY kline-gap-marker-backfill /kline-gap-marker-backfill
COPY --from=certificates /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/ca-certificates.crt

ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt

USER 65532:65532

CMD ["/kline-gap-marker-backfill", "idle"]
