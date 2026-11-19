# Recon order — first 20 minutes

## 0-2 min: baseline + headers

- `curl -sI $BASE/` — fingerprint + proxy topology.
- `curl -s $BASE/zz-no-such-9x` — save the catch-all body.

## 2-5 min: the high-value paths

/.git/HEAD /.env /robots.txt /sitemap.xml /backup.zip — the five that carry
most solves. Read bodies.

## 5-10 min: ops and framework surfaces

/actuator /server-status /phpinfo.php /.DS_Store /swagger.json + the
framework-fingerprinted debug paths (/console, /__debug__/, /_profiler,
/telescope, /actuator/env).

## 10-15 min: variants and leftovers

.env family (.env.bak/.env.old/.env.local), .swp/.bak for known files,
manifests, /logs/, status/metrics.

## 15-20 min: the 403s and hints

Each 403 → alternate-verbs/Host/path tricks. Each leaked name (comment,
header, error path) → a targeted probe.

## After 20 min

- Hits routed to their files; chains to owning classes.
- All-negative → recorded as such; done.
