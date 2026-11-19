# Hunting pop rdi — the arg0 setter


The most-needed gadget — arg0's setter:

    /R pop rdi
    pwn_triage --gadgets      # reports it when present

## The variants

- `pop rdi; ret` — the clean one.
- `pop rdi; pop rXX; ret` — a two-pop; budget the extra qword.
- `pop rdi; <side effect>; ret` — audit the tail.

## Falsifier

Absent entirely: ret2csu's edi path (r13) or a mov-based set is the
substitute.
