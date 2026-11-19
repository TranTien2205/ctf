# Key and certificate files

.pem, .key, .crt, .p12, id_rsa files: raw key material served over HTTP — the most direct disclosure there is.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| /server.key or /id_rsa or /.ssh/ | private key | use directly |
| /cert.pem or /server.crt | public cert | verify/inspect |
| /keystore.p12 or *.pfx | bundled keys | extract with openssl |

## Steps

1. Probe: /id_rsa /.ssh/id_rsa /server.key /private.key /key.pem /server.pem /cert.pem /keystore.p12.
2. A private key in the response IS the finding — use it to authenticate/decrypt.
3. Public certs: inspect for internal names (CN, SANs).
4. Bundled stores (p12/pfx) extract locally with openssl.

## Falsifier

Falsifier — no key files served: channel closed.

## Traps

- Private keys are never committed to the repo — extract, use, redact.
- A key may be passphrase-protected — note and try the usual suspects.
- SAN fields on certs leak internal hostnames.

## Commands

```bash
for p in /id_rsa /.ssh/id_rsa /server.key /key.pem; do curl -s -o /tmp/r -w "$p %{http_code} %{size_download}\n" "$BASE$p"; done
```

## Cross-references

`env-config-leaks.md` · `chaining.md`
