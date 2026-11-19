# MT19937 deep — the Mersenne Twister, end to end

## The definition

MT19937 holds a 19968-bit state as 624 words of 32 bits. Per call:

```
twist (when the index wraps every 624 outputs)
y = state[i]; temper y (4 shifts+masks); output y; i++
```

The `temper` is a fixed, invertible sequence of `^(y>>11)`, `^((y<<7)&B)`,
`^((y<<15)&C)`, `^(y>>18)`.

## Why 624 consecutive words are fatal

`temper` is a bijection on 32 bits — `untemper` exists. Feed 624
consecutive 32-bit outputs, `untemper` each, and the entire internal
state array is recovered — the future is deterministic from there.

## `mt19937-clone`

```bash
python3 tools/crypto_attack.py mt19937-clone --outputs o0,...,o623
python3 tools/crypto_attack.py mt19937-clone --outputs-file outs.txt
python3 tools/crypto_attack.py mt19937-clone --outputs-file outs.txt --count 10
```

- `--outputs` = comma-separated raw 32-bit words.
- `--outputs-file` = a file of them (cleaner for 624).
- `--count n` = emit the next `n` outputs after cloning.

## The hard requirements — all four

| Requirement | The check | If violated |
|---|---|---|
| **624** outputs | `len == 624` | state incomplete — NO clone |
| **consecutive** | no gap in the stream | alignment off — clone the wrong window |
| **raw words** | `getrandbits(32)` | float/`randint`/`mod` is post-processed |
| **no reseed** | same generator | the window crosses a reseed — alignment breaks |

## The output-shape traps — the most common failure

- **`random.random()`** returns a float `getrandbits(53)/2**53` — NOT a
  32-bit word. Cloning on floats gives garbage.
- **`randint(a,b)`/`choice`/`shuffle`** — the word is reduced/used
  internally — the observation isn't the raw word.
- **`getrandbits(k)` for `k<32`** — a truncated word; the low bits are
  dropped — not directly cloneable.
- **multiple calls interleaved** — if you collect every call's output the
  stream is consecutive; if other code also consumes the generator (a
  shared `random` module), your outputs have GAPS — the clone is off.

## The reseed trap

`random.seed(...)` called between your 624 collected outputs resets the
index — the window is no longer aligned. Detect: a discontinuity in the
output stream / a `seed` call in the request handler. Re-collect within
one contiguous window.

## The seed-search alternative

When you CAN'T get 624, ask: is the seed small? `random.seed(int(time()))`
/`random.seed(pid)` → enumerate the seed window → match an output → clone
from the matched seed. See `per-family-seed.md`.

## The verification

Hold back output 625, `mt19937-clone --count 1`, compare. `predict ==
held` is the only accept.
