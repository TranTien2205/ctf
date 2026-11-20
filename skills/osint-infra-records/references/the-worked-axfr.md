# Worked — a zone transfer

1. `--type NS` → the nameservers.
2. `--axfr --server ns1` → the whole zone spills.
3. Every hostname + record at once — including the flag host.

## Notes

- Try every listed NS — one may be permissive while others refuse.
- A successful transfer lists every name + its records — the
  subdomain map without brute-forcing.
- Refusal is normal — fall back to crt.sh SANs + wordlist brute.

## After a transfer

The zone lists every hostname — grep it for flag/secret/internal
names; query each candidate's TXT/SANs. A successful AXFR is the
full subdomain map in one shot.

## The result

A successful transfer prints every RRset — hostname + type + value; grep for flag-named names and non-operational TXT.

## The evidence

A transfer answer is verbatim zone data — the strongest subdomain evidence.
