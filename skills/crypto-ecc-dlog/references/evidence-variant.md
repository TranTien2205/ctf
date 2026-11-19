# Evidence variant — the proof requirements, restated

## The `class` evidence

A scalar `d`/`x`/`k` plus its verification transcript:

- `d=0x…` + `d·G == Q` output.
- `x=…` + `pow(g,x,p) == h` output.
- `k=…` + the recovered `d` verify.

## The `impact` evidence

`flag{...}`/`CTF{...}` read from decoded bytes — the decrypted plaintext,
the forged-request response, the DH-derived plaintext.

## The substring rule

`post-probe` checks `--evidence` is a substring of `--response` — paste the
tool output, not a paraphrase.

## The non-evidence

- A plausible scalar that doesn't verify.
- A "looks right" lattice vector without `d·G == Q`.
- The flag-shaped string the challenge *shows* you in the description.

## The record

`post-probe` → `../field-notes.md` → `classify_solve`/`attempts` — the
verbatim transcript is the proof, not the narration.
