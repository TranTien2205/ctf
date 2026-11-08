# Gadget selection: build the call, not the chain

A ROP chain is just a sequence of `pop`/`call`/`ret` gadgets arranged to make
one libc call you can't make directly. The gadgets don't matter — the *call*
does.

## The minimum gadget set

| Need | Gadget shape |
|---|---|
| load `rdi` (arg0) | `pop rdi ; ret` |
| load `rsi` (arg1) | `pop rsi ; ret` |
| load `rdx` (arg2) | `pop rdx ; ret` — rarest, often needs `pop rdx ; pop rbx` or a `mov` chain |
| call a function | `ret` into its PLT, or `call [got]` |
| fix alignment | a bare `ret` before the real gadget (16-byte SSE crash fix) |
| pivot the stack | `pop rsp`, `leave; ret`, `xchg` |

`ROPgadget --binary ./bin` or `ropper` lists them; `tools/pwn_triage.py`
names the essential ones it found.

## The three win calls

| Goal | Gadget chain |
|---|---|
| ret2win | `&win` alone |
| ret2libc `system("/bin/sh")` | `pop rdi; &"/bin/sh"; ret; &system` — needs a libc leak for `system` and the string |
| ret2plt `puts(puts@got)` then re-exploit | `pop rdi; &puts@got; ret; &puts@plt` → leaked libc, second stage |

## When there are no gadgets (short binary)

| Fallback | Idea |
|---|---|
| `ret2csu` / `__libc_csu_init` | the universal `pop rbx; rbp; r12-r15; ret` + `call` sequence every glibc-linked binary has |
| `ret2plt` | call a PLT stub whose GOT the binary already populated |
| `ret2dlresolve` | fake a `link_map`/`reloc` so the dynamic linker resolves `system` for you |
| SROP | `syscall; sigreturn` sets *all* registers from the stack at once |
| JOP / COP | no `ret`-ending gadgets — use `jmp [reg]`/`call [reg]` dispatch |

## The leak-first rule

ASLR + PIE mean no absolute address is known — one leak kills both. The leak
is always the first gadget: `puts(puts@got)` or `printf`/`write` of a GOT/
link-map address, then re-exploit with the computed base.

## Falsifier

No `pop`/`call`/`ret`/`syscall` gadgets exist at all — a fully static,
stripped, gadget-poor binary with no libc to call. The overflow must land
somewhere else (stack pivot to a controlled region, or a different bug
entirely).

## Traps

- `pop rdx` is the scarce one — check for it *before* planning a 3-arg call;
  fall back to one-arg calls or a `mov` gadget.
- On 64-bit the alignment crash is at `movaps` in `system`/`do_system` —
  insert one bare `ret` to fix it.
- A `ret`-chain that crashes midway usually hit an unmapped `call [reg]` —
  verify every gadget's target is actually mapped before sending.
