# Real-world cases deep — the attacks that shipped

## Debian OpenSSL weak keys (CVE-2008-0166)

The `md_rand` line removal left `pid` as the only entropy — ~32k possible
keys per arch. The seed-search shape at scale: enumerate `pid` ∈
`[0,32768]` → derive each candidate key → match. The window bound was the
pid range itself. This is the canonical "bounded seed → enumerate"
attack.

## PHP `mt_rand`/`mt_srand` token attacks

`mt_srand(seed)` with a small or leaked seed → `mt_rand` outputs are
predictable. `mt_rand` is PHP's MT19937 — same family, but the SEEDING
and the `MT_RAND_PHP` output mode differ from Python's `random`. The
fingerprint: `mt_rand`/`mt_srand` in the source → the PHP variant, not a
naive `random` clone.

## `java.util.Random` — the standard LCG

`m=2^48`, `a=0x5DEECE66D`, `c=0xB`. `nextInt()` returns `x >> 16` — the
top bits. `lcg-truncated --low-bits 16` with the KNOWN `a`,`c`,`m`. Used
in session tokens, game seeds, UUID-like ids across Java codebases.

## `drand48`/`lrand48`/`erand48`

The C `*48` family — same `a`,`m` as `java.util.Random`, `lrand48` leaks
`x >> 17`. Same `lcg-truncated` shape, `low-bits=17`.

## `Math.random` — V8's `xorshift128+`

V8/Chrome's `Math.random` is `xorshift128+` — `s0+s1` — plus a `double`
conversion (`[0,1)`). NOT `xorshift128` — `xorshift128.py` returns a
wrong state. The fingerprint: the `+` variant + the float output. Used in
client-side token/id generation — a real browser-session attack.

## glibc `rand()` — the additive generator

`rand()` isn't a plain LCG — it's `TYPE_3` additive feedback (`x_i =
x_{i-31} + x_{i-3} mod 2^32`). The `lcg-*` attacks miss; the state is 31
words of history. A "rand()" label is not automatically an LCG —
fingerprint the structure.

## Windows `rand()`/`MSVCRT`

`rand()` = `x = x*214013 + 2531011 mod 2^32; return (x>>16)&0x7fff` — a
truncated LCG. `lcg-truncated` with `m=2^32, a=214013, c=2531011,
low-bits=17` (32-15=17... actually `>>16 & 0x7fff` keeps bits 16-30, the
model differs — the mask shape matters).

## `srand(time(0))` — the classic

Every `srand(time(0))`/`mt_srand(time())`/`new Random(currentTimeMillis)`
is a bounded-seed case. The window is the issue epoch — the search is
seconds wide.

## The takeaway

The real-world cases are the SAME families — LCG, LFSR, MT, xorshift,
seed — with platform-specific constants and output shapes. The skill is
recognizing the family + the platform variant, then meeting its count
and normalization gates.
