# 5. Privacy-preserving operator metrics

Olace keeps aggregate operator metrics: enough to know that tunnels reconnect too often or that time-to-first-token regressed, structured so that they cannot describe a person. There is no user analytics profile, no event stream per account, and no identifier in any metric.

## The allowlist model

The whole system is defined by one catalog, mirrored byte-for-byte in three codebases and published in this repo:

- [metrics/catalog-backend.py](../metrics/catalog-backend.py) (the ingestion authority)
- [metrics/catalog-daemon.go](../metrics/catalog-daemon.go)
- [metrics/catalog-flutter.dart](../metrics/catalog-flutter.dart)

Every metric name, every dimension key, and every allowed dimension value is a bounded enum declared in the catalog. Ingestion runs `clean_dims_for_metric` (see the backend catalog): a report whose metric is unknown, whose dimension key is undeclared, or whose value is outside the declared vocabulary is dropped. There is no free-text field anywhere in the pipeline, so an identifier or content string cannot enter the pipeline even from a buggy client.

What a metric can say: `chat.ttft{route=local, le=2000}` incremented by one. What a metric cannot say: who, which conversation, from which device, from which IP. Those columns do not exist.

## Aggregation

Clients report counter increments; the backend folds them into rollup rows keyed by metric, dimensions and time bucket. Rollups are the only stored form. Latency-style metrics are histograms with fixed bucket bounds declared in the catalog.

## Direct Mode

Direct Mode is Olace's Maximum Privacy setting: conversations that never touch the backend beyond transport. Such conversations may emit exactly one metric: `chat.security_mode`, a counter that says a Direct Mode conversation happened. Nothing else about such a conversation is reported, including the performance metrics that other routes emit. This rule is stated in the client catalog itself and enforced in the clients.

## Keeping the published copies current

`python3 metrics/check_sync.py` (run in this repo's CI) verifies the daemon and app catalogs are exact name subsets of the backend catalog. Each private repo has a `check-transparency` target that byte-diffs its live catalog file against the copy here, so the published catalog cannot silently lag what ships.
