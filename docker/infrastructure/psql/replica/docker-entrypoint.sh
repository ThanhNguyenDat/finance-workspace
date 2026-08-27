#!/bin/bash
set -e

# Set default if not defined
SLOT_DB=${SLOT_DB:-replication_slot_1}
PG_SERVICE_HOSTNAME=${PG_SERVICE_HOSTNAME:-primary}

echo "Starting backup ${SLOT_DB} from ${PG_SERVICE_HOSTNAME}..."

if [ -d "/var/lib/postgresql/data" ] && [ "$(ls -A /var/lib/postgresql/data)" ]; then
  echo "Data directory already exists. Skipping backup."
else
  # Wait for pg_basebackup to succeed
  until pg_basebackup --pgdata=/var/lib/postgresql/data -R --slot="${SLOT_DB}" --host="${PG_SERVICE_HOSTNAME}" --port=5432
  do
    echo "Waiting for primary to connect..."
    sleep 1s
  done

  echo "Backup done"
  chmod 0700 /var/lib/postgresql/data
fi

echo "Starting replica..."
exec postgres -c hot_standby_feedback=on
# You can also add more configs if needed:
# exec postgres -c hot_standby_feedback=on -c max_standby_streaming_delay=5min -c track_commit_timestamp=on
