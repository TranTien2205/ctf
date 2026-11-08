# Format string: leak first, write second

`printf(user_input)` gives two primitives: `%x`/`%p` reads up the stack,
`%n` writes a count into a pointer taken from the stack. Leak before writing —
a write without a known target and offset is a crash.

## Step 1 — find the offset

```text
AAAA.%x.%x.%x.%x.%x.%x.%x.%x
```

Look for `41414141` in the output — that position is where the format
function's argument pointer meets your input. On 64-bit it's typically
argument 6+; direct-access form `AAAA.%6$p` confirms it.

## Step 2 — the read primitive

| Specifier | Reads |
|---|---|
| `%p` / `%x` | the value at that stack slot |
| `%s` | the *string at* the pointer in that slot — deref |
| `%6$s`, `%7$s` | direct deref of a chosen slot |

To read an arbitrary address: place the address itself in the input, then
`%<off>$s` where `<off>` is the slot that holds it — the format function
follows your pointer. This is how a flag string or a canary is leaked.

## Step 3 — the write primitive

`%n` writes "number of bytes printed so far" into the pointer at a slot:

```text
[pad to reach value] %<off>$n    -> writes that count to *slot_off
```

The width tricks that build the count: `%<N>x` pads the output to N before
`%n` — so `%<N>x%<off>$n` writes N. Two-byte writes (`%hn`) and one-byte
writes (`%hhn`) per address avoid huge output for large values; write the
target address into the input and hit it with `%hhn` one byte at a time.

`pwntools`' `fmtstr_payload(offset, {addr: value})` generates the whole thing.

## The win paths

| Writable target | Becomes |
|---|---|
| GOT entry (partial RELRO) | next call jumps to your address |
| return address on the stack | one `%n` per byte, or `%hn` halves |
| a function pointer / hook (`__malloc_hook` on old libc) | shellcode/one_gadget on next call |
| a length or flag variable | "authenticated" without a hijack |

## Falsifier

The input is printed through a constant format (`printf("%s", buf)`) or the
conversion specifiers are stripped — `%x` echoes literally on every position.

## Traps

- The offset shifts with input length — fix the format string's length before
  counting `%x` positions, or use the `AAAA` marker to locate it.
- `%s` on a slot that isn't a pointer crashes — probe with `%p` first to see
  which slots hold addresses.
- 64-bit arguments go in registers first: `%x` positions 1-5 are rdi..r9
  territory; the stack-sourced input usually starts at `%6$p`.
