# The .well-known and meta-file layer — case catalogue

security.txt, humans.txt, crossdomain.xml, clientaccesspolicy.xml, assetlinks.json: the standards-defined info files.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | /security.txt | contact/scope | sometimes key links |
| 2 | /crossdomain.xml or clientaccesspolicy.xml | Flash-era policy | permissive policy = a finding |
| 3 | /.well-known/ paths | standard endpoints | openid config, jwks |
| 4 | /humans.txt or /favicon.ico unusual | dev artifacts | team/version hints |

## Falsifier

Falsifier — none of the standard paths exist: the layer is absent.
