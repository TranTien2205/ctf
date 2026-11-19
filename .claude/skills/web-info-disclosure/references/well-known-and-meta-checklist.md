# The .well-known and meta-file layer — checklist

security.txt, humans.txt, crossdomain.xml, clientaccesspolicy.xml, assetlinks.json: the standards-defined info files.

## Checklist

- [ ] Probe: /security.txt /.well-known/security.txt /crossdomain.xml /clientaccesspolicy.xml /humans.txt /.well-known/openid-configuration.
- [ ] crossdomain.xml with * policy is a real misconfig finding.
- [ ] .well-known/openid-configuration maps the whole auth surface.
- [ ] jwks_uri from the config → the signing keys (sometimes symmetric→asymmetric confusion).

## Abort conditions

- openid-configuration is a route map for the whole OAuth surface.
- crossdomain.xml '*' lets any site read the API — old but still found.
- humans.txt sometimes names the framework/version.

## Falsifier

Falsifier — none of the standard paths exist: the layer is absent.
