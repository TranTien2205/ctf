# The live cert — SANs + subject + issuer

`openssl s_client -connect host:443` — the cert's Subject, Issuer,
and the SAN list — the sibling hostnames; plus validity dates.

## The command

    openssl s_client -connect host:443 -servername host </dev/null 2>/dev/null | openssl x509 -noout -text

The Subject, Issuer, and the X509v3 Subject Alternative Name —
the sibling hostnames in one read.
