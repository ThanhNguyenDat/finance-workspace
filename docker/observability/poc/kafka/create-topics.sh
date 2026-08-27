#!/bin/sh
# Topics are created explicitly, never by auto-creation. The spec versions
# schema through the topic suffix, so an accidentally auto-created topic would
# silently bypass the versioning contract.
#
# PARTITIONS/REPLICATION here are POC values on a single broker. Production
# requires replication factor 3 with min.insync.replicas=2 and acks=all -- see
# poc/README.md, "What this POC does not prove".
set -eu

BOOTSTRAP="${KAFKA_BOOTSTRAP:-kafka:9092}"
PARTITIONS="${TOPIC_PARTITIONS:-3}"
REPLICATION="${TOPIC_REPLICATION:-1}"
RETENTION_MS="${TOPIC_RETENTION_MS:-259200000}" # 3 days, the low end of the spec's 3-7 day target

echo "waiting for ${BOOTSTRAP}"
until /opt/kafka/bin/kafka-broker-api-versions.sh --bootstrap-server "$BOOTSTRAP" >/dev/null 2>&1; do
  sleep 2
done

create() {
  topic="$1"; shift
  /opt/kafka/bin/kafka-topics.sh --bootstrap-server "$BOOTSTRAP" \
    --create --if-not-exists \
    --topic "$topic" \
    --partitions "$PARTITIONS" \
    --replication-factor "$REPLICATION" \
    --config "retention.ms=${RETENTION_MS}" \
    --config compression.type=zstd \
    "$@"
  echo "ready: $topic"
}

create observability.logs.raw.v1
create observability.logs.canonical.v1
# The DLQ keeps data longer than the transport topics: a poison event has to
# stay readable long enough for someone to actually triage it.
create observability.logs.dlq.v1 --config retention.ms=604800000
create observability.traces.v1
# Business facts are not diagnostics. They get their own retention because
# losing one is a lost trade record, not a lost log line.
create analytics.trading.events.v1 --config retention.ms=604800000

/opt/kafka/bin/kafka-topics.sh --bootstrap-server "$BOOTSTRAP" --list
