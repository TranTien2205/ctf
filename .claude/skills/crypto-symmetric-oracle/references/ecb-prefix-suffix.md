# ECB prefix vs suffix oracles

Byte-at-a-time works when your input PRECEDES the secret (suffix). When the secret precedes your input, the method inverts — recover backwards, or via a fixed suffix oracle.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| encrypt(input || secret) | suffix oracle | standard byte-at-a-time |
| encrypt(secret || input) | prefix oracle | reverse byte-at-a-time |
| encrypt(prefix || input || suffix) | sandwiched | combined alignment+suffix |

## Steps

1. Determine which of the three shapes you have by injecting a marker and watching where it lands relative to the fixed blocks.
2. Suffix: standard byte-at-a-time — pad so the unknown byte ends your block.
3. Prefix: recover right-to-left — put your marker AFTER the secret region and build guesses from the tail.
4. Sandwiched: measure both fixed lengths, handle alignment for prefix, then run byte-at-a-time on the suffix.

## Falsifier

Falsifier — neither prefix nor suffix is controllable (your input is wholly inside fixed material): the oracle doesn't reach the secret.

## Traps

- A random per-request prefix only defeats alignment, not the method — if a fixed suffix exists, attack backwards.
- Prefix recovery is rarer; double-check your orientation before implementing.
- Multiple secrets in one ciphertext can be independent — measure each region separately.

## Commands

```bash
python3 tools/ecb_oracle.py --url 'https://target/enc?pt={PT}' --bs 16 --resp hex
```

## Cross-references

`ecb-byte-at-a-time.md` · `block-alignment.md`
