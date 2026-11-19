# Detection checklist variant — the reads, by shape

## The bare-blob checklist

- [ ] the charset — `+/=`/hex/`01`/`.-`/`ADFGVX` → `enc_detect`/`other-ciphers`
- [ ] `cipher_id --text` — IC/chi²/Kasiski/freq/verdict
- [ ] the IC — ~0.066/0.038/0.05
- [ ] the chi² — `k`/flat/reversed
- [ ] Kasiski — the `L`
- [ ] the freq — ETAOIN/reversed/flat/scrambled
- [ ] the family → `classical_solve`

## The named-cipher checklist

- [ ] the name — `caesar`/`vigenere`/`playfair`/`adfgvx`/`hill`
- [ ] `other-ciphers.md` — `classical_solve` covers `caesar`,`vigenere`,
      `subst`,`atbash`,`railfence` only
- [ ] a script / dcode.fr for the named others
- [ ] `cipher_id` confirms the family (the IC/digraph/`ADFGVX` shape)

## The layered checklist

- [ ] `cipher_id` → layer → decode → `cipher_id` on the output → repeat
- [ ] `enc_detect` per encoding layer
- [ ] the innermost — `flag{`/`CTF{`

## The short-blob checklist

- [ ] the `flag{`/`CTF{`/`SNT{`/`synt{`/`Pxl{` positions — the crib
- [ ] the common letters — `σ(E)`/`σ(T)`/`k`/`key`
- [ ] `classical_solve` polishes — the stats unreliable under ~30 chars

## The `flag{`-visible checklist

- [ ] `flag{`/`CTF{`/`SNT{`/`synt{`/`Pxl{`/`fhpnf{` — the crib
- [ ] `known-plaintext.md` — `σ`/`k`/`key`/`π` from the positions
- [ ] `classical_solve` confirms the decode

## The verify

`pt` language + `enc(pt)=ct` — `verify*.md`.
