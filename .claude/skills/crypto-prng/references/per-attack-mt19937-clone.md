# Per-attack `mt19937-clone` — the card

## Trigger

Python `random`/`numpy.random` MT19937 with **624 consecutive 32-bit
outputs** — the full state window.

## Command

```bash
python3 tools/crypto_attack.py mt19937-clone \
  --outputs o0,o1,...,o623
python3 tools/crypto_attack.py mt19937-clone \
  --outputs-file outs.txt --count 10
```

## Mechanism

`mt19937.predict_next` — untemper each of the 624 outputs into the state
array, then roll the MT forward. **The 624 is exact — 623 is one word
short, not one output short.**

## Verify

`predict_next` reproduces a held-back 32-bit word exactly.

## Falsifiers

- <624 words → the state is underdetermined — NO clone.
- outputs not consecutive raw words → temper/unpacking mismatches.
- `predict != held-back` → wrong count, wrong endianness, or not MT.

## Boundaries

- `random.random()` floats → `int(v * 2**53)` recovers a `getrandbits(53)`
  pair — NOT a raw 32-bit word; use `getrandbits(32)` outputs.
- `randint`/`choice` mix outputs — not raw words; recover differently.
- Only the full 19968-bit state clones; partial windows don't.
- The 624 must be CONSECUTIVE — a gap breaks the index alignment.
