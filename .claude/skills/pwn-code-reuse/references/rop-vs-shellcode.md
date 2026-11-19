# ROP vs shellcode — when NX is off


If a writable+executable page exists, shellcode beats a chain — simpler,
no gadget hunt.

## Check

python3 tools/pwn_triage.py ./chal — the NX line; an RWX segment in
the dm maps.

## The choice

- RWX present or NX off: `python3 tools/sc_gen.py execve64 --raw` the
  stub, jump into it.
- NX on: the chain.

## Falsifier

Both exist — prefer shellcode for simplicity.
