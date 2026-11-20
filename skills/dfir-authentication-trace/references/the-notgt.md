# The missing-TGT anomaly — NTLM where Kerberos is normal

An NTLM network logon (AuthenticationPackageName NTLM) for an account
that normally authenticates with Kerberos, with no matching 4768/4769
pair on the DC, is the stolen-credential-shaped anomaly — the package
plus the absent ticket pair together are the answer shape.

## The anomaly

NTLM + no TGT = the shape to flag, not a package alone.
