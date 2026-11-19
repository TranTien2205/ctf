# RELRO and the GOT — the write question


- Partial RELRO: the GOT stays writable — GOT[x] can be overwritten to
  redirect a call.
- Full RELRO (BIND_NOW): the GOT is mapped read-only after init —
  GOT writes crash.

## Check

python3 tools/pwn_triage.py ./chal — the RELRO line names it.

## The route difference

- Partial: GOT overwrite redirects an import's next call.
- Full: GOT is read-only — the chain must end at a call that goes
  through existing targets (system via PLT call, a function).

## Falsifier

None — a routing fact.
