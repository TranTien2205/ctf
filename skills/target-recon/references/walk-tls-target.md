# Worked example: tls-target

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Walked: supplied https://<host>:8443.

1. tls-certfields: openssl s_client -> self-signed, CN
   'challenge-ctf', SANs none (tls-sanlist negative).
2. alpn -> h2 negotiated (prot-http2 note).
3. Standard https intake follows - the cert facts are recorded
   observations, not blockers.
4. Observations: self-signed-fresh-infra, h2 enabled, single
   SAN-free cert = single-purpose instance (ctf-instancepattern).
## Pivot

Signal harvested -> out-*; route named -> that skill.
