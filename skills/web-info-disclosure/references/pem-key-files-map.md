# Key and certificate files — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| /server.key or /id_rsa or /.ssh/ | private key | use directly |
| /cert.pem or /server.crt | public cert | verify/inspect |
| /keystore.p12 or *.pfx | bundled keys | extract with openssl |

## Falsifier

Falsifier — no key files served: channel closed.
