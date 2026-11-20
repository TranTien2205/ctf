# Reading the live cert

    openssl s_client -connect host:443 -servername host </dev/null

Subject, Issuer, SANs, validity — the SAN list is the sibling
leak; the Issuer names the CA.

## What to read

- Subject — the primary name.
- Issuer — the CA.
- X509v3 Subject Alternative Name — the sibling list.
- Validity dates — the window.
The SAN list is usually the highest-value field.
