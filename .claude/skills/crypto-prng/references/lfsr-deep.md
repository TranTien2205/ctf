# LFSR deep — the linear feedback shift register, end to end

## The definition

An LFSR of width `w` is a register of `w` bits. Each clock:

```
new_bit = XOR of the bits at the tap positions
shift the register left/right; the new_bit enters at one end;
the bit leaving the other end is the output.
```

The taps define the feedback polynomial. Width `w` and taps `t` fully
characterize the generator — the whole future is `w` bits of state.

## Why the state is recoverable

The recurrence is **linear over GF(2)**. `w` consecutive output bits pin
the register exactly — the future is a linear function of those `w` bits.
With the taps unknown, `2w` bits let Berlekamp-Massey recover the minimal
recurrence (the taps), then the register.

## `berlekamp-massey` — recover the taps

Given a bitstream `b0,b1,...`, BM finds the shortest linear recurrence
(the minimal LFSR) that generates it. Output: the connection polynomial →
the `(width, taps)` pair.

```bash
python3 tools/crypto_attack.py berlekamp-massey --bits 0,1,1,0,...
python3 tools/crypto_attack.py berlekamp-massey --keystream-hex deadbeef...
python3 tools/crypto_attack.py berlekamp-massey --bits-file bits.txt
```

- Needs ≥`2·w` bits for a width-`w` LFSR; more is better.
- Input forms are exclusive: `--bits` (comma list) OR `--keystream-hex`
  OR `--bits-file`.
- Expected signal: a `(width, taps)` whose linear complexity is « the
  stream length. A complexity ≈ stream length means NOT a plain LFSR.
- Falsifier: linear complexity ≈ half the stream = a random stream → not
  an LFSR → wrong class.

## `lfsr-recover` — reconstruct the register

With the bits and the width (and optionally the taps), reconstruct the
register state.

```bash
python3 tools/crypto_attack.py lfsr-recover --bits b0,... --width w
python3 tools/crypto_attack.py lfsr-recover --bits b0,... --taps t --width w
```

- `--taps` is optional: without it the tool derives taps via BM.
- Expected signal: the register + the tap set.

## `lfsr-predict` — roll it forward

With taps and width, roll the register forward `n` steps to emit the next
`n` output bits.

```bash
python3 tools/crypto_attack.py lfsr-predict \
  --bits b0,... --taps t --width w --count n
```

- `--taps` and `--width` are REQUIRED here.
- `--count n` = how many future bits to emit.
- Expected signal: the next `n` bits; verify against held-back bits.
- Falsifier: predicted bits diverge from held-back → wrong taps/width.

## The tap convention — the trap

`--taps` uses **1-indexed from the LSB**. Tap list `[w, k]` in the tool
means positions counted from the output bit. Different writeups index
from 0 or from the MSB — a wrong convention inverts/shifts the taps and
the predicted bits diverge. If `lfsr-predict` fails on known-correct
bits, flip the convention.

## The stream-cipher connection

An LFSR alone is a bad cipher — linear, so `2w` known keystream bits are
fatal. Real stream ciphers add a **nonlinear combiner** or **filter**
over several LFSRs. BM on that output gives a HIGH linear complexity —
the signal you're facing a combiner, not a plain LFSR (then: correlation
attack, not this module).

## The verification

Hold back `k` keystream bits, `lfsr-predict --count k`, compare.
`predict == held` is the only accept.
