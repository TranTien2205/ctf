# Cloud recon: providerid

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Cloud provider identification: DNS CNAME
(amazonaws.com, azurewebsites.net, cloudapp.net, googleapis,
elb.amazonaws.com), headers (x-amz-*, x-azure-*, x-goog-*,
x-ms-*), error-page signatures, TLS cert issuers (Amazon,
Google Trust Services, Microsoft), IP whois/ASN (pasv-asn).
The provider names which metadata/bucket surfaces exist.
## Pivot

Signal harvested -> out-*; route named -> that skill.
