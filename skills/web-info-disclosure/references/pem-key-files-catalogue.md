# Key and certificate files — case catalogue

.pem, .key, .crt, .p12, id_rsa files: raw key material served over HTTP — the most direct disclosure there is.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | /server.key or /id_rsa or /.ssh/ | private key | use directly |
| 2 | /cert.pem or /server.crt | public cert | verify/inspect |
| 3 | /keystore.p12 or *.pfx | bundled keys | extract with openssl |

## Falsifier

Falsifier — no key files served: channel closed.
