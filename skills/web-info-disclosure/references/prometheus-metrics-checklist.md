# Prometheus /metrics mining — checklist

A /metrics endpoint is a topology map: service names, queue names, error counts, request rates — and occasionally a flag-leaking label.

## Checklist

- [ ] Fetch /metrics; read every metric name and label.
- [ ] Custom app metrics name internal components, queues, endpoints.
- [ ] Label values occasionally carry tokens, paths, user ids.
- [ ] The metric names tell you what the app does internally — recon.

## Abort conditions

- Pushgateway/node_exporter paths also leak (/metrics on :9100 is out of scope).
- A /metrics with auth 403 is still a service boundary worth noting.

## Falsifier

Falsifier — no /metrics or it's stripped to standard runtime counters only: nothing extra disclosed.
