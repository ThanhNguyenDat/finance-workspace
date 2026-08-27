#!/bin/sh
# Synthetic ECS JSONL producer, standing in for a real Finance service.
#
# It writes to stdout/stderr only -- exactly what the spec requires of an
# application -- and never talks to Kafka itself. The node agent picks the
# lines up off the Docker json-file stream.
#
# Three shapes are emitted on purpose, so the stack demonstrates all three
# processor outcomes without needing production traffic:
#   1. valid  -> observability.logs.canonical.v1
#   2. poison -> observability.logs.dlq.v1  (missing required fields)
#   3. secret -> canonical, with the credential redacted
set -eu

SERVICE_NAME="${SERVICE_NAME:-finance-mw}"
SERVICE_ENV="${SERVICE_ENV:-development}"
SERVICE_VERSION="${SERVICE_VERSION:-0000000000000000000000000000000000000000}"
INTERVAL="${EMIT_INTERVAL_SECONDS:-2}"

# service.instance.id must be unique per process. The container hostname is the
# nearest stable per-instance identity available inside the container.
INSTANCE_ID="$(cat /etc/hostname)"

uuid() { cat /proc/sys/kernel/random/uuid; }
# BusyBox date has no %N, so sub-second precision is not available here.
# Whole-second RFC 3339 UTC is still a valid @timestamp; a real service uses
# its language's RFC3339Nano formatter.
now()  { date -u +%Y-%m-%dT%H:%M:%SZ; }
hex()  { head -c "$1" /dev/urandom | od -An -tx1 | tr -d ' \n' | cut -c1-"$2"; }

emit_valid() {
  level="$1"; msg="$2"; stream="$3"
  trace_id="$(hex 32 32)"
  span_id="$(hex 16 16)"
  line=$(printf '{"@timestamp":"%s","log":{"level":"%s"},"message":"%s","service":{"name":"%s","environment":"%s","version":"%s","instance":{"id":"%s"}},"event":{"id":"%s","dataset":"%s.application","kind":"event"},"trace":{"id":"%s"},"span":{"id":"%s"},"http":{"request":{"id":"%s"}}}' \
    "$(now)" "$level" "$msg" "$SERVICE_NAME" "$SERVICE_ENV" "$SERVICE_VERSION" \
    "$INSTANCE_ID" "$(uuid)" "$SERVICE_NAME" "$trace_id" "$span_id" "$(uuid)")
  if [ "$stream" = "stderr" ]; then printf '%s\n' "$line" >&2; else printf '%s\n' "$line"; fi
}

# Missing event.id, service.name and service.instance.id: the processor must
# reject this and produce exactly one DLQ record, then keep consuming.
emit_poison() {
  printf '{"@timestamp":"%s","log":{"level":"info"},"message":"poison event with no identity"}\n' "$(now)"
}

# A credential in the message body. The canonical record must show [REDACTED];
# if the raw value ever reaches ClickHouse or S3, redaction has regressed.
emit_secret() {
  printf '{"@timestamp":"%s","log":{"level":"warn"},"message":"upstream auth retry authorization=Bearer NOTAREALTOKEN_synthetic_marker_0123456789 done","service":{"name":"%s","environment":"%s","version":"%s","instance":{"id":"%s"}},"event":{"id":"%s","dataset":"%s.application","kind":"event"}}\n' \
    "$(now)" "$SERVICE_NAME" "$SERVICE_ENV" "$SERVICE_VERSION" "$INSTANCE_ID" "$(uuid)" "$SERVICE_NAME"
}

echo "loadgen: service=${SERVICE_NAME} env=${SERVICE_ENV} instance=${INSTANCE_ID}" >&2

i=0
while :; do
  i=$((i + 1))
  emit_valid info  "portfolio decision evaluated candidate=$i" stdout
  emit_valid debug "kline batch consumed count=$((i * 17))"   stdout
  [ $((i % 5)) -eq 0 ] && emit_valid error "broker rejected order attempt=$i" stderr
  [ $((i % 7)) -eq 0 ] && emit_poison
  [ $((i % 11)) -eq 0 ] && emit_secret
  sleep "$INTERVAL"
done
