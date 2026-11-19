# Evidence map — artifact → what it proves → the gate

## The artifact → proof → gate

| Artifact | Proves | Gate |
|---|---|---|
| collected outputs | the stream exists | — |
| generator fingerprint | a hypothesis | — |
| `gcd`→`m` | affine structure | then `lcg-recover` |
| BM `(w,taps)` | an LFSR recurrence | then `lfsr-predict` |
| `predict==held` | **the state is real** | class evidence |
| forged token works | **exploit** | impact evidence |
| `flag{` in response | **the flag** | `pre-flag` |

## The proof hierarchy

```
outputs < fingerprint < predict==held < impact < flag{
        hypothesis      class           impact  the flag
```

Only `predict==held` and up are recordable evidence. Below it is
hypothesis.

## The `post-probe` gate

```bash
tools/hooks.py post-probe <ch> --verdict confirms --hypothesis-id <id> \
  --class crypto-prng --evidence-kind class|impact \
  --evidence 'predict_next == held_back' --response '<bytes>'
```

`--evidence` MUST be a substring of `--response` — the gate checks.

## The `pre-flag` gate

```bash
tools/hooks.py pre-flag <ch> --value 'flag{...}' --evidence '<the bytes>'
```

The flag comes from the response/artifact — never from the description.

## What each file covers

| File | Coverage |
|---|---|
| `evidence*.md` | the ladder + the gates |
| `verify*.md` | the `predict==held` protocol |
| `field-notes-*` | the record format |
| `verified-chains*.md` | the honest status |
| `negative-results*.md` | the falsifier records |
