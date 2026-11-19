# First-contact commands — the fmtstr triage


## Sequence

    python3 tools/pwn_triage.py ./chal
    r2 -A ./chal ; afl | grep -i printf
    echo '%p.%p.%p' | ./chal
    echo 'AAAAAAAA.%7\$p' | ./chal

## Reading

- pwn_triage: RELRO/PIE/canary decide the target routes.
- afl | grep printf: the call sites.
- %p reflection: the primitive confirmed.
- the marker: the arg offset.

## Falsifier at first contact

'%p' echoes literally (not a pointer): the input isn't the format —
closed at this site.
