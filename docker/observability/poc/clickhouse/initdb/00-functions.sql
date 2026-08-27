-- OTLP encodes resource attributes as [{"key":"service.name","value":{"stringValue":"x"}}].
-- A named function keeps the span materialized view readable.
CREATE FUNCTION IF NOT EXISTS attr_value AS (resource_span, wanted) ->
    JSONExtractString(
        arrayFirst(
            kv -> JSONExtractString(kv, 'key') = wanted,
            JSONExtractArrayRaw(JSONExtractRaw(resource_span, 'resource'), 'attributes')
        ),
        'value', 'stringValue'
    );
