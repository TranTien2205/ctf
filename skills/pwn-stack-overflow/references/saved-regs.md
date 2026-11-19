# Saved registers — the frame layout

The stack frame: [locals][canary?][saved RBP][saved RIP][args]. Smashing past saved RBP hits saved RIP — the offset math lives here.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| saved RIP holds your bytes | return control | p64(target) |
| saved RBP corrupted | frame chain | leave;ret pivot |

## Steps

1. Standard frame: input buffer at the bottom, then locals, canary (if any), saved RBP, saved RIP.
2. Offset to saved RIP = offset to saved RBP + 8 (x64).
3. Corrupting saved RBP enables the leave;ret pivot.
4. Corrupting saved RIP = return control.

## Falsifier

Falsifier — the write stops before the saved registers: the bound is too short; check the read's bound.

## Traps

- The canary (if any) sits between locals and saved regs — corrupting it trips __stack_chk_fail.
- Frame layout varies with optimization — measure, don't assume the textbook layout.

## Commands

```bash
r2 -A ./chal && pdf @ <func>
```

## Cross-references

`offset-measurement.md` · `canary-bypass.md`
