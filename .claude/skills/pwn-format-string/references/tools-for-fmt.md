# The tools — pwn_triage + radare2 + cyclic


No dedicated fmtstr tool — the primitives are the specifiers. pwn_triage
names the protections (RELRO decides GOT), r2 finds the call site.

```bash
python3 tools/pwn_triage.py ./chal   # RELRO decides GOT
r2 -A ./chal && pdf @ <func>          # the printf call site
python3 tools/pwn_cyclic.py --find <bytes>  # if it composes a smash
```

## Steps

1. pwn_triage ./chal — RELRO decides if GOT is writable.
2. r2 -A && pdf @ <func> — the printf call and its format position.
3. Find the arg offset: AAAA.%N$p sweep.
4. If it composes a smash, cyclic measures that offset.

## Falsifier

No printf call takes your input as the format: the class is closed.
