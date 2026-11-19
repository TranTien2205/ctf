# Is the heap executable? — the NX question


The heap is NX on any modern build — shellcode on the heap doesn't
execute; the heap's value is pointers and metadata, not code.

## Check

python3 tools/pwn_triage.py ./chal — the NX line; `r2 -d` + `dm` shows
the region's perms.

## The consequence

All heap techniques end at a POINTER write, not a code landing — the
redirect jumps to existing code (system, a gadget, a win function).

## Falsifier

No writable code region and no pointer-write target: the heap gives
leaks only — combine with another class for exec.
