#!/usr/bin/env bash
set -Eeuo pipefail

usage() {
  printf 'usage: classify-codex-result.sh <exit-status> <stdout-jsonl> <stderr-log>\n' >&2
  exit 2
}

[ "$#" -eq 3 ] || usage
status="$1"
stdout_log="$2"
stderr_log="$3"
[[ "$status" =~ ^[0-9]+$ ]] || usage
[ -f "$stdout_log" ] || usage
[ -f "$stderr_log" ] || usage

if [ "$status" -eq 0 ]; then
  printf '%s\n' success
  exit 0
fi
if [ "$status" -eq 124 ]; then
  printf '%s\n' timeout
  exit 0
fi

structured="$(
  {
    jq -rs '
      [.. | objects | to_entries[]?
        | select(.key | test("^(code|type|category|error_type|reason)$"; "i"))
        | .value | strings]
      | join(" ") | ascii_downcase
    ' "$stdout_log" 2>/dev/null || true
    jq -Rrs '
      [split("\n")[] | fromjson?
        | .. | objects | to_entries[]?
        | select(.key | test("^(code|type|category|error_type|reason)$"; "i"))
        | .value | strings]
      | join(" ") | ascii_downcase
    ' "$stderr_log" 2>/dev/null || true
  } | tr '\n' ' '
)"
messages="$(
  {
    jq -rs '
      [.. | objects | to_entries[]?
        | select(.key | test("^(message|detail|type|status)$"; "i"))
        | .value | strings]
      | join(" ") | ascii_downcase
    ' "$stdout_log" 2>/dev/null || true
    tr '[:upper:]' '[:lower:]' <"$stderr_log"
  } | tr '\n' ' '
)"

matches() {
  local value="$1"
  local pattern="$2"
  [[ "$value" =~ $pattern ]]
}

if matches "$structured" '(^|[[:space:]])(insufficient_quota|quota_exhausted|global_quota_exhausted|account_quota_exhausted|usage_limit_reached|credits_exhausted)([[:space:]]|$)'; then
  result=global-quota-exhausted
elif matches "$structured" '(^|[[:space:]])(model_not_found|model_unavailable|unsupported_model|model_routing_failure)([[:space:]]|$)'; then
  result=model-unavailable
elif matches "$structured" '(^|[[:space:]])(model_capacity_exceeded|model_limit_reached|model_rate_limit_exceeded|model_usage_limit)([[:space:]]|$)'; then
  result=model-specific-limit
elif matches "$structured" '(^|[[:space:]])(rate_limit_exceeded|too_many_requests|http_429)([[:space:]]|$)'; then
  result=transient-rate-limit
elif matches "$structured" '(^|[[:space:]])(authentication_error|invalid_api_key|unauthorized|permission_denied)([[:space:]]|$)'; then
  result=auth-error
elif matches "$structured" '(^|[[:space:]])(network_error|connection_error|dns_error|tls_error)([[:space:]]|$)'; then
  result=network-error
elif matches "$structured" '(^|[[:space:]])(timeout|request_timeout|deadline_exceeded)([[:space:]]|$)'; then
  result=timeout
elif matches "$structured" '(^|[[:space:]])(implementation_error|worker_failed|task_failed)([[:space:]]|$)'; then
  result=implementation-error
elif matches "$messages" '(global|account(-wide)?)[[:space:]_-]*(codex[[:space:]_-]*)?quota[^.]{0,80}(exhausted|depleted|reached|exceeded)' \
  || matches "$messages" '(quota|usage[[:space:]_-]*limit)[^.]*(exhausted|depleted)[^.]*(account|global)' \
  || matches "$messages" 'usage[[:space:]_-]*limit[^.]{0,80}(exhausted|depleted)' \
  || matches "$messages" '(account|session)[[:space:]_-]*(usage[[:space:]_-]*)?(cap|limit)[^.]{0,80}(reached|exceeded|exhausted)' \
  || matches "$messages" 'no[[:space:]]+remaining[[:space:]]+(quota|credits)'; then
  result=global-quota-exhausted
elif matches "$messages" '(selected[[:space:]_-]*)?model[^.]{0,80}(not[[:space:]_-]*found|unavailable|not[[:space:]_-]*available|unsupported|routing[[:space:]_-]*failure)'; then
  result=model-unavailable
elif matches "$messages" 'model[^.]{0,80}(capacity|specific[[:space:]_-]*limit|usage[[:space:]_-]*limit)[^.]{0,80}(exceeded|reached|unavailable|full)' \
  || matches "$messages" '(capacity|limit|quota)[^.]{0,80}for[[:space:]]+(the[[:space:]]+)?(selected[[:space:]]+)?model'; then
  result=model-specific-limit
elif matches "$messages" '(^|[^0-9])429([^0-9]|$)|too[[:space:]_-]*many[[:space:]_-]*requests|rate[[:space:]_-]*limit'; then
  result=transient-rate-limit
elif matches "$messages" '(^|[^0-9])(401|403)([^0-9]|$)|authentication|unauthorized|invalid[[:space:]_-]*(api[[:space:]_-]*)?key|permission[[:space:]_-]*denied'; then
  result=auth-error
elif matches "$messages" 'network[[:space:]_-]*error|connection[[:space:]_-]*(failed|reset|refused)|dns|enotfound|tls[[:space:]_-]*(error|failure)|could[[:space:]]+not[[:space:]]+resolve'; then
  result=network-error
elif matches "$messages" 'timed[[:space:]_-]*out|timeout|deadline[[:space:]_-]*exceeded'; then
  result=timeout
elif matches "$messages" 'implementation[[:space:]_-]*error|worker[[:space:]_-]*failed|task[[:space:]_-]*failed|"status"[[:space:]]*:[[:space:]]*"failed"'; then
  result=implementation-error
else
  result=unknown-error
fi

printf '%s\n' "$result"
