# Naming the sink — which call is the bug — checklist

Companion to `the-sink-name.md`.

## Checklist

- [ ] Before the offset, name the sink: which call does the unchecked copy?
- [ ] gets/strcpy/scanf %s/sprintf are the unbounded set; read/memcpy with an
- [ ] influenced n are the controllable set; fgets is bounded unless its arg
- [ ] is wrong.
- [ ] `grep -nE 'gets|strcpy|strcat|scanf|sprintf|vsprintf|read|memcpy' src.c`
- [ ] names every candidate; the bound-checking arg at each decides which is
- [ ] the bug.
- [ ] Every candidate's bound is correctly enforced: no stack-corruption sink
- [ ] exists in this source.
