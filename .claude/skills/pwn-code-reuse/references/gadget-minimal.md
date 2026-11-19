# Minimal gadget sets — the survival chain


When only a few gadgets exist, the chain must be minimal:

- A single `pop rdi; ret` + a win function = enough.
- No pop gadgets at all: ret2csu, or a jmp/call gadget that uses
  existing register state.
- Only `syscall`: needs the regs settable some other way (prior
  program state).

## The search

    python3 tools/pwn_triage.py ./chal --gadgets
    r2 -A ./chal ; /R pop

## Falsifier

The gadget set can't express any useful call: the class's write must
aim at a different mechanism (a full override of a bigger structure).
