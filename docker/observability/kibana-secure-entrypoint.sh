#!/usr/bin/env bash
set -euo pipefail

# The Kibana Docker entrypoint converts setting-shaped environment variables
# into command-line flags. Keep credentials and encryption keys out of argv by
# moving them to a private, ephemeral Kibana keystore before starting Kibana.
readonly source_config_dir="${FINANCE_KIBANA_SOURCE_CONFIG_DIR:-/usr/share/kibana/config}"
readonly runtime_config_dir="${FINANCE_KIBANA_RUNTIME_CONFIG_DIR:-/tmp/finance-kibana-config}"
readonly kibana_bin_dir="${FINANCE_KIBANA_BIN_DIR:-/usr/share/kibana/bin}"
readonly kibana_docker_entrypoint="${FINANCE_KIBANA_DOCKER_ENTRYPOINT:-/usr/local/bin/kibana-docker}"

if [[ "$runtime_config_dir" != "/tmp/finance-kibana-config" ]]; then
  printf 'Refusing unsafe Kibana runtime config directory\n' >&2
  exit 2
fi

required_secret_names=(
  FINANCE_KIBANA_ELASTICSEARCH_PASSWORD
  FINANCE_KIBANA_SECURITY_ENCRYPTION_KEY
  FINANCE_KIBANA_REPORTING_ENCRYPTION_KEY
  FINANCE_KIBANA_SAVED_OBJECTS_ENCRYPTION_KEY
)

for secret_name in "${required_secret_names[@]}"; do
  secret_value="${!secret_name:-}"
  if [[ ${#secret_value} -lt 32 || ! "$secret_value" =~ ^[A-Za-z0-9_-]+$ ]]; then
    printf 'Kibana secret %s must be at least 32 safe characters\n' \
      "$secret_name" >&2
    exit 2
  fi
done

if [[ -n "${KIBANA_DECRYPTION_ONLY_KEY:-}" && \
  ( ${#KIBANA_DECRYPTION_ONLY_KEY} -lt 32 || \
    ! "$KIBANA_DECRYPTION_ONLY_KEY" =~ ^[A-Za-z0-9_-]+$ ) ]]; then
  printf 'KIBANA_DECRYPTION_ONLY_KEY must be empty or at least 32 safe characters\n' >&2
  exit 2
fi

umask 077
rm -rf -- "$runtime_config_dir"
install -d -m 700 "$runtime_config_dir"
if [[ -f "$source_config_dir/kibana.yml" ]]; then
  install -m 600 "$source_config_dir/kibana.yml" \
    "$runtime_config_dir/kibana.yml"
else
  : >"$runtime_config_dir/kibana.yml"
  chmod 600 "$runtime_config_dir/kibana.yml"
fi

if [[ -n "${KIBANA_DECRYPTION_ONLY_KEY:-}" ]]; then
  printf '\nxpack.encryptedSavedObjects.keyRotation.decryptionOnlyKeys: ["%s"]\n' \
    "$KIBANA_DECRYPTION_ONLY_KEY" >>"$runtime_config_dir/kibana.yml"
fi

export KBN_PATH_CONF="$runtime_config_dir"
"$kibana_bin_dir/kibana-keystore" create >/dev/null
printf '%s' "$FINANCE_KIBANA_ELASTICSEARCH_PASSWORD" |
  "$kibana_bin_dir/kibana-keystore" add --stdin --force elasticsearch.password >/dev/null
printf '%s' "$FINANCE_KIBANA_SECURITY_ENCRYPTION_KEY" |
  "$kibana_bin_dir/kibana-keystore" add --stdin --force xpack.security.encryptionKey >/dev/null
printf '%s' "$FINANCE_KIBANA_REPORTING_ENCRYPTION_KEY" |
  "$kibana_bin_dir/kibana-keystore" add --stdin --force xpack.reporting.encryptionKey >/dev/null
printf '%s' "$FINANCE_KIBANA_SAVED_OBJECTS_ENCRYPTION_KEY" |
  "$kibana_bin_dir/kibana-keystore" add --stdin --force \
    xpack.encryptedSavedObjects.encryptionKey >/dev/null
chmod 600 "$runtime_config_dir/kibana.yml" "$runtime_config_dir/kibana.keystore"

unset FINANCE_KIBANA_ELASTICSEARCH_PASSWORD FINANCE_KIBANA_SECURITY_ENCRYPTION_KEY \
  FINANCE_KIBANA_REPORTING_ENCRYPTION_KEY FINANCE_KIBANA_SAVED_OBJECTS_ENCRYPTION_KEY \
  KIBANA_DECRYPTION_ONLY_KEY FINANCE_KIBANA_SOURCE_CONFIG_DIR \
  FINANCE_KIBANA_RUNTIME_CONFIG_DIR FINANCE_KIBANA_BIN_DIR \
  FINANCE_KIBANA_DOCKER_ENTRYPOINT secret_name secret_value

exec "$kibana_docker_entrypoint"
