# The bounded sweep — scope discipline — operational checklist

Info-disclosure sweeps are bounded by definition: a short list of well-known paths, not a scanner. The class lives inside the supplied surface.

## Checklist

- [ ] Baseline the catch-all first — every later read diffs against it.
- [ ] Run the canonical list: /.git/HEAD /.env /robots.txt /sitemap.xml /backup.zip /actuator /server-status /.DS_Store /phpinfo.php /swagger.json + framework debug.
- [ ] Read every response, not just status.
- [ ] Add ONLY paths the evidence names (comment refs, header hints, error paths) — no invented names.

## Abort conditions

- Directory brute-forcing (ffuf/gobuster wide) is not this class — it's a scope violation on shared infra.
- A path you invent has no evidence to stand on — don't probe it.
- The sweep is once per target; re-run only when new evidence names a path.

## Falsifier

Falsifier — canonical list all-negatives AND no evidence names a custom path: the disclosure surface is closed.

## Cross-references

`exposed-artifacts.md` · `catchall-falsifier.md`
