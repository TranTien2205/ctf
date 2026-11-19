# Health and readiness endpoints — checklist

/health, /healthz, /ready, /live: orchestration endpoints that range from 'ok' to a full dependency map.

## Checklist

- [ ] Probe /health /healthz /ready /live /startup.
- [ ] A detailed health response names databases, queues, upstreams — the topology.
- [ ] Failed dependency statuses name what's down and where it lives.
- [ ] Minimal 'ok' answers close this channel fast.

## Abort conditions

- Detail level varies wildly — read the whole body once.
- k8s-style /healthz often includes component-level detail.
- A health endpoint that checks the DB gives a reachability oracle.

## Falsifier

Falsifier — bare ok/404 across all health paths: nothing leaked.
