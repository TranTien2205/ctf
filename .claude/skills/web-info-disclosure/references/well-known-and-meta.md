# The .well-known and meta-file layer

security.txt, humans.txt, crossdomain.xml, clientaccesspolicy.xml, assetlinks.json: the standards-defined info files.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| /security.txt | contact/scope | sometimes key links |
| /crossdomain.xml or clientaccesspolicy.xml | Flash-era policy | permissive policy = a finding |
| /.well-known/ paths | standard endpoints | openid config, jwks |
| /humans.txt or /favicon.ico unusual | dev artifacts | team/version hints |

## Steps

1. Probe: /security.txt /.well-known/security.txt /crossdomain.xml /clientaccesspolicy.xml /humans.txt /.well-known/openid-configuration.
2. crossdomain.xml with * policy is a real misconfig finding.
3. .well-known/openid-configuration maps the whole auth surface.
4. jwks_uri from the config → the signing keys (sometimes symmetric→asymmetric confusion).

## Falsifier

Falsifier — none of the standard paths exist: the layer is absent.

## Traps

- openid-configuration is a route map for the whole OAuth surface.
- crossdomain.xml '*' lets any site read the API — old but still found.
- humans.txt sometimes names the framework/version.

## Commands

```bash
for p in /security.txt /crossdomain.xml /.well-known/openid-configuration /humans.txt; do curl -s -o /tmp/r -w "$p %{http_code} %{size_download}\n" "$BASE$p"; done
```

## Cross-references

`header-disclosure.md` · `robots-sitemap.md`
