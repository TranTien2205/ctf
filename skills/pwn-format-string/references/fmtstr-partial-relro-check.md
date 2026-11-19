# Confirming partial RELRO before the GOT write


The GOT write needs partial RELRO (GOT writable). pwn_triage reports it
— don't guess.

## Steps

1. python3 tools/pwn_triage.py ./chal — the RELRO line.
2. Partial: GOT stays writable — %n-to-GOT works.
3. Full: GOT readonly — the write crashes; use ret-addr/hook instead.

## Verify

    python3 tools/pwn_triage.py ./chal
    readelf -d ./chal | grep -iE 'bind_now|relro'

## Falsifier

The report says full RELRO: GOT writes crash on contact.
