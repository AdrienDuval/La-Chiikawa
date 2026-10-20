#!/usr/bin/env bash
# Set up Garage once: layout, buckets, app key. Safe to run again.
set -euo pipefail
export MSYS_NO_PATHCONV=1   # Git Bash on Windows: don't rewrite /garage into a Windows path

BUCKETS="bronze silver gold mlflow"
KEY_NAME="chiikawa-app"

garage() { docker compose exec -T garage /garage "$@"; }

echo "Waiting for Garage..."
for i in $(seq 1 30); do
  garage status >/dev/null 2>&1 && break
  if [ "$i" -eq 30 ]; then echo "Garage did not answer after 30s"; garage status; exit 1; fi
  sleep 1
done


if garage status | grep -q "NO ROLE ASSIGNED"; then
  NODE_ID=$(garage node id -q | cut -d@ -f1)
  echo "Assigning layout to node $NODE_ID"
  garage layout assign -z dc1 -c 10G "$NODE_ID"
  garage layout apply --version 1
fi

for bucket in $BUCKETS; do
  garage bucket info "$bucket" >/dev/null 2>&1 || garage bucket create "$bucket"
done

if ! garage key info "$KEY_NAME" >/dev/null 2>&1; then
  echo "Creating key $KEY_NAME: copy the Key ID and Secret into .env"
  garage key create "$KEY_NAME"
fi

for bucket in $BUCKETS; do
  garage bucket allow --read --write "$bucket" --key "$KEY_NAME"
done

echo "Garage is ready."
garage bucket list
