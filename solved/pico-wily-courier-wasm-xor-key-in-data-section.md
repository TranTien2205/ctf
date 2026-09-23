# wily-courier (picoCTF) — SOLVED (self-solved)

- Platform: picoCTF. `http://wily-courier.picoctf.net:<port>/index.html`
  (the port changes per instance spin-up).
- Date: 2026-09-23
- Stack: Apache 2.4.38, a static page, an obfuscated JS shim, a 942-byte WebAssembly module
- Flag: redacted; verified by the challenge's own `check_flag()` returning 1
- Assistance: none.

## The JS is a shim, not the challenge

`index.html` pulls `rTEuOmSfG3.js`, which is string-array obfuscated. Deobfuscated
it is about six lines:

```js
let r = await fetch('./qCCYI0ajpD');
let mod = await WebAssembly.instantiate(await r.arrayBuffer());
exports = mod.instance.exports;

function onButtonPress() {
    let v = document.getElementById('input').value;
    for (let i = 0; i < v.length; i++) exports.copy_char(v.charCodeAt(i), i);
    exports.copy_char(0, v.length);                       // null terminator
    exports.check_flag() == 1 ? "Correct!" : "Incorrect!";
}
```

Nothing is checked server-side and nothing is hashed — the whole decision is one
call into a 942-byte WASM module.

## The module hands over everything

No `wasm2wat`, `wasm-objdump` or `wasmer` on this box, and none were needed:
node has WebAssembly built in, and the module exports its own internals.

```
memory, __wasm_call_ctors, strcmp, check_flag, input, copy_char, key,
__dso_handle, __data_end, __global_base, __heap_base, __memory_base, __table_base
```

`strcmp` plus a `key` global says the comparison is over bytes in the data
section rather than a computed digest. Reading the globals:

```
input      = 0x430
key        = 0x42b
__data_end = 0x530
```

A first pass scanning the low 4 KB for printable runs found nothing, which was
the useful negative result: the data is not stored in the clear. Dumping the
actual region shows why:

```
0x0400  9d 6e 93 c8 b2 b9 41 8b 94 90 dd 3e 94 97 90 dd
0x0410  3f c4 c2 c9 dd 34 c2 c5 97 db 31 93 92 c0 da 36
0x0420  93 93 c1 d9 3e 91 c1 97 90 00 00 f1 a7 f0 07 ed
```

41 bytes of ciphertext at `0x400`, then the 5-byte key `f1 a7 f0 07 ed` at
`0x42b`, then the input buffer at `0x430`.

## The key is applied backwards

A straight repeating XOR with `f1 a7 f0 07 ed` produces garbage. Solving for the
key from the known prefix instead of guessing settles it immediately — the flag
must start `picoCTF{`, so:

```
ct[0]=0x9d ^ 'p'=0x70 -> 0xed   = key[4]
ct[1]=0x6e ^ 'i'=0x69 -> 0x07   = key[3]
ct[2]=0x93 ^ 'c'=0x63 -> 0xf0   = key[2]
ct[3]=0xc8 ^ 'o'=0x6f -> 0xa7   = key[1]
ct[4]=0xb2 ^ 'C'=0x43 -> 0xf1   = key[0]
```

so `plaintext[i] = ct[i] ^ key[4 - (i mod 5)]` — the key is consumed in reverse
byte order. XORing with the reversed key decodes all 41 bytes.

## Verified, not assumed

The recovered string was fed back through the module's own interface —
`copy_char` per character, null terminator, then `check_flag()`:

```
check_flag(flag)    = 1
check_flag(one char changed) = 0
check_flag("nope")  = 0
```

## Reusable lessons

- **A WASM flag checker usually exports its own data pointers.** Before reaching
  for a disassembler, instantiate it and print the globals: `key`, `input`,
  `__data_end` name the exact bytes worth dumping, and `strcmp` in the export
  list already tells you the check is a byte comparison rather than a digest.
- **A failed printable-string scan is a result, not a dead end.** It says the
  comparison data is encoded, which narrows the next step to finding the key
  rather than hunting for more strings.
- **Solve a repeating XOR from the known prefix instead of trying orderings.**
  The flag format gives five known plaintext bytes, which recovers the key
  schedule directly and exposes the reversal in one step.
- **Verify through the challenge's own validator when it is callable.** Decoding
  to something that looks like a flag is weaker evidence than the checker
  returning 1 for it and 0 for a one-character variant.

---

## Second variant, same host — solved 2026-09-23

Another challenge behind the same `wily-courier.picoctf.net` name, on a different
port. Same shell — obfuscated JS shim, `copy_char` / `check_flag`, a WASM module
— but the module is 2142 bytes instead of 942 and, decisively, **exports no
`key`**:

```
memory, __wasm_call_ctors, strcmp, check_flag, input, copy_char,
__dso_handle, __data_end, __global_base, __heap_base, __memory_base, __table_base
```

Memory holds 41 ciphertext bytes at `0x400` and nothing else. The transform is in
the code, so the first variant's trick — read the key, XOR, done — does not apply.

### The transform is observable without reading it

`check_flag()` rewrites the input buffer **in place**. That turns the algorithm
into a black box that can be queried: write bytes with `copy_char`, call
`check_flag`, then read `0x430` back and see what it produced.

A dependency matrix over all 41 input positions showed influence travelling
strictly forward, with no global mixing — `in[40]` touches only `out[40]`,
`in[20]` touches nothing below 20. That shape is what a linear function looks
like, so linearity was **tested rather than assumed**: for `T(x) = M·x + c`,
flipping one input bit yields one column of `M`, and a two-bit flip must equal
the XOR of the two corresponding columns. Three such checks passed.

328 single-bit probes (41 bytes x 8 bits) recovered the whole matrix, after which

    T(answer) = ct   =>   M·(answer ^ base) = ct ^ T(base)

is an ordinary GF(2) solve. Rank came out 328 of 328, so the solution is unique.
The algorithm was never reverse-engineered.

### check_flag is a weak oracle — do not verify with it alone

The stored ciphertext contains `0x00` at index 28, so `strcmp` compares only the
first 28 bytes. Everything after that is unconstrained: a variant with the
39th character replaced still returned 1.

Two verification mistakes were made and caught here:

1. Testing several candidates against **one** WASM instance. Since `check_flag`
   transforms the buffer in place, the second call runs on already-transformed
   data. Every test needs a fresh instantiation.
2. Comparing a 65-byte memory slice against the 41-byte result and reading the
   length mismatch as a failed match.

The real check is byte equality over the full 41: `transform(answer)` matched the
stored ciphertext with no differing byte.

Flag: redacted; a different flag from the first variant.

### Reusable lessons (new)

- **An in-place transform is a free oracle.** When a checker rewrites its own
  input buffer, the algorithm can be characterised by querying it, which is
  often much cheaper than disassembling it.
- **Test linearity, do not assume it.** A forward-only dependency matrix suggests
  linearity; a multi-bit flip agreeing with the XOR of single-bit columns
  establishes it. Once established, the whole problem becomes a solve.
- **A NUL inside the expected value silently truncates a strcmp check.** The
  verdict function then accepts many wrong answers, so confirm against the full
  stored value rather than against the verdict.
