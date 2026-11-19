# Saved registers — the frame layout — checklist

The stack frame: [locals][canary?][saved RBP][saved RIP][args]. Smashing past saved RBP hits saved RIP — the offset math lives here.

## Checklist

- [ ] Standard frame: input buffer at the bottom, then locals, canary (if any), saved RBP, saved RIP.
- [ ] Offset to saved RIP = offset to saved RBP + 8 (x64).
- [ ] Corrupting saved RBP enables the leave;ret pivot.
- [ ] Corrupting saved RIP = return control.

## Abort conditions

- The canary (if any) sits between locals and saved regs — corrupting it trips __stack_chk_fail.
- Frame layout varies with optimization — measure, don't assume the textbook layout.

## Falsifier

Falsifier — the write stops before the saved registers: the bound is too short; check the read's bound.
