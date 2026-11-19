# Redirect and Location-header disclosure — deep

302s leak internal URLs; redirect chains reveal routing structure and sometimes unauthenticated intermediate content.

## Boundary conditions

- Every positive read diffs against the catch-all baseline; status alone proves nothing.
- A 403 on a real path is a candidate bypass (verbs/Host/path) — try before recording dead.
- Content found is evidence; its use is the owning class's job.
- Artifacts containing secrets are handled, not committed.

## Falsifier

Falsifier — redirects go straight to public pages: nothing hidden.

## Highest-cost traps

- --no-follow on probes keeps the 302 oracle — the redirect IS the signal.
- Location to an internal host is a vhost find.
- A redirect that leaks a token in the Location query = session disclosure.

## Commands

```bash
curl -s -D- -o /dev/null '$BASE/admin'
```

## Cross-references

`response-anatomy.md` · `header-disclosure.md`
