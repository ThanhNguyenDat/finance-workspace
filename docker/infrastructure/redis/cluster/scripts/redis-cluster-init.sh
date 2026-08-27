#!/bin/bash
set -e

HOSTNAME=$(hostname)
REDIS_PORT=6379
CLUSTER_NODES=(
  "finance-redis-cluster-node1:6379"
  "finance-redis-cluster-node2:6379"
  "finance-redis-cluster-node3:6379"
  "finance-redis-cluster-node4:6379"
  "finance-redis-cluster-node5:6379"
  "finance-redis-cluster-node6:6379"
)

echo "Starting Redis server on $HOSTNAME..."

redis_cmd() {
  redis-server \
    --port "$REDIS_PORT" \
    --cluster-enabled yes \
    --cluster-config-file nodes.conf \
    --cluster-node-timeout 5000 \
    --appendonly yes \
    --protected-mode no
}

wait_for_node() {
  local NODE=$1
  local HOST=${NODE%:*}
  local PORT=${NODE#*:}

  until redis-cli -h "$HOST" -p "$PORT" ping | grep -q PONG; do
    echo "Node $NODE is not ready. Waiting..."
    sleep 1
  done
}

init_cluster() {
  echo "Checking cluster state..."

  if redis-cli cluster info 2>/dev/null | grep -q "cluster_state:ok"; then
    echo "Cluster already initialized."
    return
  fi

  echo "Creating Redis Cluster..."
  yes yes | redis-cli --cluster create \
    "${CLUSTER_NODES[@]}" \
    --cluster-replicas 1

  echo "Redis cluster created successfully."
}

###
### MAIN
###

# Node1 runs Redis in background so we can run cluster init
if [ "$HOSTNAME" = "finance-redis-cluster-node1" ]; then
  redis_cmd &
  sleep 3

  echo "Waiting for all Redis nodes to be up..."
  for NODE in "${CLUSTER_NODES[@]}"; do
    wait_for_node "$NODE"
  done

  echo "All nodes are up."
  init_cluster

  wait -n  # Wait for redis-server background
else
  # Other nodes run normally (foreground)
  redis_cmd
fi
