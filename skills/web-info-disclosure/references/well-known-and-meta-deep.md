# The .well-known and meta-file layer — deep

security.txt, humans.txt, crossdomain.xml, clientaccesspolicy.xml, assetlinks.json: the standards-defined info files.

## Boundary conditions

- Every positive read diffs against the catch-all baseline; status alone proves nothing.
- A 403 on a real path is a candidate bypass (verbs/Host/path) — try before recording dead.
- Content found is evidence; its use is the owning class's job.
- Artifacts containing secrets are handled, not committed.

## Falsifier

Falsifier — none of the standard paths exist: the layer is absent.

## Highest-cost traps

- openid-configuration is a route map for the whole OAuth surface.
- crossdomain.xml '*' lets any site read the API — old but still found.
- humans.txt sometimes names the framework/version.

## Commands

```bash
for p in /security.txt /crossdomain.xml /.well-known/openid-configuration /humans.txt; do curl -s -o /tmp/r -w "$p %{http_code} %{size_download}\n" "$BASE$p"; done
```

## Cross-references

`header-disclosure.md` · `robots-sitemap.md`
