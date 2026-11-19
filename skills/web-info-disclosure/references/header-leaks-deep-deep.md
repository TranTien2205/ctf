# Deep header analysis — beyond Server/X-Powered-By — deep

The secondary headers: ETag shapes, X-Cache, Via, timing headers, framework session-cookie names — each a fingerprint.

## Boundary conditions

- Every positive read diffs against the catch-all baseline; status alone proves nothing.
- A 403 on a real path is a candidate bypass (verbs/Host/path) — try before recording dead.
- Content found is evidence; its use is the owning class's job.
- Artifacts containing secrets are handled, not committed.

## Falsifier

Falsifier — stripped headers and generic cookies: framework must come from body/error analysis.

## Highest-cost traps

- Cookie names are the most reliable framework fingerprint — can't be stripped as easily.
- X-Cache/Via chains map to request-smuggling's proxy topology.
- Duplicate/conflicting headers are themselves a finding.

## Commands

```bash
curl -s -D- -o /dev/null '$BASE/' | sort
```

## Cross-references

`header-disclosure.md` · `response-anatomy.md`
