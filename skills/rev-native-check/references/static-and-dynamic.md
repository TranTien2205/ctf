# Native check: static first, dynamic only where static ends

A native deciding check is a function that says yes/no. Find it statically;
if static reading runs out (obfuscation, self-modifying, data-dependent
branching), drive it dynamically — but only far enough to see the answer.

## Static path — the fastest three moves

1. `tools/pwn_triage.py` or `checksec` → arch, PIE, protections, interesting
   imports (`strcmp`, `memcmp`, `strncmp`, `verify`, `check`).
2. `strings -a -t x ./bin | grep -iE 'flag|correct|wrong|input|usage'` →
   the messages around the check.
3. Disassemble the function that prints "wrong" — the deciding compare is
   almost always within a few instructions of the failure string.

```bash
objdump -d -M intel ./bin | grep -A30 'call.*strcmp\|call.*memcmp'
radare2 -q -c 'aaa; afl~check; afl~main; pdf @main' ./bin
```

The compare that matters: a constant vs your input, a transformed constant
(xor table, rol/substitution) vs your input, or a computed digest/hash
compared to a stored one.

## The three check shapes

| Shape | The attack |
|---|---|
| byte-by-byte compare | read the constant — answer is in `.rodata` |
| transformed compare (xor/permute) | run the inverse on the constant |
| hash/digest compare | can't invert — patch the jump, or find where the digest is computed |

## Dynamic path — where static ends

`gdb`/`ltrace`/`strace` only after the static map:

```bash
ltrace ./bin < input           # library calls + the compare arguments live
gdb -q ./bin
  b *<addr-of-cmp>             # break on the deciding instruction
  run < input
  x/s $rsi                     # the value being compared to
```

The fastest dynamic answer: break at the compare, read both operands — the
correct input is usually sitting in a register or a memory operand.

## Anti-analysis

`ptrace` self-checks, `timing` checks, self-modifying code, and opaque
predicates all end the static path — the answer is to drive them dynamically
or emulate the function (`unicorn`, `angr`) rather than to defeat the check
head-on.

## Falsifier

No deciding compare exists — the input is never checked against a constant,
transform, or digest, and the "wrong" path is just a default print. The bug
is in what the input *does*, not what it's checked against — route to the
pwn classes instead.

## Traps

- `strings` misses constructed strings (xor-assembled, `mov`-built) — check
  the disassembly around the print calls.
- A VM or heavy obfuscation hides the compare; look for the single branch
  that decides the final yes/no, not the whole function.
- 64-bit args: `rdi`,`rsi`,`rdx`,`rcx` — `strcmp`'s args are the first two;
  a `call strcmp` with `x/s $rdi, x/s $rsi` usually prints both halves of
  the answer.
