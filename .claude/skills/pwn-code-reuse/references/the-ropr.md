# The ROP reporter — what pwn_triage gives


python3 tools/pwn_triage.py ./chal --gadgets reports the essential
set: pops, syscall, ret, leave, mov-store — the presence/absence that
decides the route before a manual search.

## The use

The triage's gadget report + protections = the route decision's
input.
