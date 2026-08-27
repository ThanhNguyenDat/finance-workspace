# Observability logging standard

This rule applies to `finance-web`, `finance-mw`, `finance-live-action`,
`finance-broker`, and `mt5`.

## Event format

- Emit one JSON object per line (JSONL) for application and access events.
- Use an RFC 3339 UTC `@timestamp`.
- Every application event must include `log.level`, `message`, `service.name`,
  `service.environment`, `service.instance.id`, `event.id`, and
  `event.dataset`.
- `event.id` is a new UUID for each event. It is not a process or request ID.
- Correlated HTTP events use the active OpenTelemetry `trace.id` and `span.id`;
  `http.request.id` remains the independent transport request ID. Correlated
  gRPC events use the same OpenTelemetry fields plus an independent
  `rpc.request.id`. Never substitute a request UUID for an OpenTelemetry trace
  ID: W3C trace IDs are 32 lowercase hexadecimal characters and span IDs are 16.
- Preserve a valid upstream `X-Request-ID` (maximum 128 characters); otherwise
  generate a UUID and return it to the caller.
- Access events include the method, path without query parameters, response
  status, duration in nanoseconds when the runtime supports it, and client
  address when available.

## Streams and files

- Send levels below `ERROR` to stdout and `ERROR` or above to stderr.
- Keep access events on stdout.
- Persist separate rotated files under `/data/log/<service>/`:
  `debug.jsonl`, `info.jsonl`, `error.jsonl`, `application.jsonl`,
  `access.jsonl`, `stdout.jsonl`, and `stderr.jsonl`.
- A runtime may add `warn.jsonl` where `WARN` is a first-class level.
- Rotate service files at each UTC day boundary and retain no archive older
  than seven days. A 10 MB size rotation may remain as a safety cap, but it
  does not replace the required daily rotation. Docker's `json-file` driver
  uses 10 MB with three files.
- Native server error logs that cannot emit JSON, such as Nginx `error_log`,
  use `error.log` and stderr; do not label plain text as JSONL.

## Safety and signal quality

- Never log credentials, API keys, tokens, cookies, authorization headers,
  request/response bodies, or full URLs containing query parameters.
- Do not emit routine access events for health, readiness, or metrics probes.
- Log exceptions with their stack trace and the active request/trace ID.
- Do not merge stderr into stdout in entrypoints or process supervisors.
- Avoid duplicate access events from framework defaults after installing the
  shared access middleware.

## Metrics endpoint

- Expose Prometheus text only at `/metrics` for every HTTP metrics surface.
- Point central vmagent scrapes, Compose healthchecks, setup-agent hooks,
  dashboards, alerts, and production verification at `/metrics`.
- Do not add framework-specific aliases such as `/actuator/prometheus`; a
  legacy request must not become a second metrics contract.

## Distributed tracing

- Propagate W3C Trace Context and Baggage across causal HTTP, gRPC, and Kafka
  boundaries. Kafka carries `traceparent`/`tracestate` in message headers;
  never add tracing data to the canonical market-event payload.
- Send traces through OTLP to one upstream OpenTelemetry Collector gateway.
  Keep SDK head sampling at 100% so the gateway can retain complete error and
  slow traces; perform bounded tail sampling at the gateway.
- Do not connect unrelated background work into one artificial trace. A Kafka
  producer-to-consumer trace is separate from an HTTP request unless that
  request causally published the message.
- Span attributes must remain low-cardinality and must not contain credentials,
  authorization/cookie headers, request or message payloads, query strings,
  account secrets, or raw stack-local environment values.
- Tracing is trace-only: Prometheus metrics continue through `/metrics` to
  VictoriaMetrics, and ECS JSONL logs continue through Filebeat to
  Elasticsearch/Kibana. Do not duplicate those signals through OTLP.

## Verification and delivery

- Every ecosystem repository must provide executable `scripts/setup-log.sh`
  and `scripts/setup-agent.sh`, include both in its runtime image, call them
  from its entrypoint, and guard that contract with a bounded test. A central
  collector integration uses an explicit no-op setup-agent hook rather than
  embedding credentials in repository source.
- Verify code and repository configuration locally before read-only production
  inspection.
- Add tests for schema fields, UUID generation, request-ID preservation, stream
  routing, and middleware behavior.
- Validate every Compose file after changing shared logging anchors.
- Commit every change, push it through GitHub Actions, deploy through Coolify,
  and verify the exact commit SHA in GitHub and production.
- Never edit production files through SSH.
