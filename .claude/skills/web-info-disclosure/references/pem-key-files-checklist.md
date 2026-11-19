# Key and certificate files — checklist

.pem, .key, .crt, .p12, id_rsa files: raw key material served over HTTP — the most direct disclosure there is.

## Checklist

- [ ] Probe: /id_rsa /.ssh/id_rsa /server.key /private.key /key.pem /server.pem /cert.pem /keystore.p12.
- [ ] A private key in the response IS the finding — use it to authenticate/decrypt.
- [ ] Public certs: inspect for internal names (CN, SANs).
- [ ] Bundled stores (p12/pfx) extract locally with openssl.

## Abort conditions

- Private keys are never committed to the repo — extract, use, redact.
- A key may be passphrase-protected — note and try the usual suspects.
- SAN fields on certs leak internal hostnames.

## Falsifier

Falsifier — no key files served: channel closed.
