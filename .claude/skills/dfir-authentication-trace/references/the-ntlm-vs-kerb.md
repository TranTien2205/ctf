# NTLM vs Kerberos — the package field

`AuthenticationPackageName` NTLM/Kerberos/Negotiate; `KeyLength` is
always 0 for Kerberos even via Negotiate; 4776 is NTLM validation
and names only the source workstation — never the destination.

## The package

KeyLength 0 = Kerberos even via Negotiate.
