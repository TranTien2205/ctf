# The bounded sweep — scope discipline — playbook

Info-disclosure sweeps are bounded by definition: a short list of well-known paths, not a scanner. The class lives inside the supplied surface.

## Ordered playbook

1. Baseline the catch-all first — every later read diffs against it.
2. Run the canonical list: /.git/HEAD /.env /robots.txt /sitemap.xml /backup.zip /actuator /server-status /.DS_Store /phpinfo.php /swagger.json + framework debug.
3. Read every response, not just status.
4. Add ONLY paths the evidence names (comment refs, header hints, error paths) — no invented names.

## Falsifier

Falsifier — canonical list all-negatives AND no evidence names a custom path: the disclosure surface is closed.

## Commands

```bash
for p in /.git/HEAD /.env /robots.txt /sitemap.xml /backup.zip /actuator /server-status /.DS_Store /phpinfo.php /swagger.json; do code=$(curl -s -o /tmp/r -w '%{http_code}' --max-time 8 "$BASE$p"); echo "$p $code $(wc -c </tmp/r)"; done
```
