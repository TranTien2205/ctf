# Confirming a sibling

A SAN or NS-named sibling — query its A/TXT/ANY, check its cert —
a sibling only counts once confirmed to resolve.

## The confirmation

- A/AAAA — does it resolve?
- TXT — a planted flag on the sibling.
- Its own SANs — further names.
- NXDOMAIN vs NODATA — nonexistent vs no-that-type.
An unresolvable SAN is a name, not a host.
