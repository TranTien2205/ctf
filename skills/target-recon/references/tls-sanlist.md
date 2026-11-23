# TLS recon: sanlist

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

SAN list: every DNS name the cert covers -
openssl x509 -noout -text | grep -A1 'Subject Alternative
Name'. Wildcards (*., internal names, sibling apps) feed the
vhost candidate list directly. Record the SAN list verbatim.
## Pivot

Signal harvested -> out-*; route named -> that skill.
