# Detection playbook variant — the discriminate, by family

## The `caesar` playbook

1. `cipher_id` — IC ~0.066, chi² one min `k`.
2. `classical_solve caesar --text` — the `k` row.
3. `pt` language → `c = p + k` — the flag.

## The `atbash` playbook

1. `cipher_id` — IC ~0.066, reversed ETAOIN.
2. `classical_solve atbash --text` — `c = 25 - p`.
3. `pt` language → `c = 25 - p` — the flag.

## The `subst` playbook

1. `cipher_id` — IC ~0.066, flat chi², ETAOIN-shaped.
2. `classical_solve subst --text [--restarts --iters]` — the `σ`.
3. A near-decode `gLAG{` — the `flag{` positions pin `σ`.
4. `pt` language → `c = σ(p)` — the flag.

## The `vigenere` playbook

1. `cipher_id` — IC ~0.038, Kasiski `L`.
2. `classical_solve vigenere --text [--keylen L|--key <word>]` — `L` cosets.
3. `pt` language → `c_i = p_i + k_{i mod L}` — the flag.

## The `railfence`/`π` playbook

1. `cipher_id` — IC ~0.05-0.066, scrambled letters.
2. `classical_solve railfence --text` — the depth `r`.
3. `n = r·c` → a columnar/route — a script.
4. `pt` language → `c = π(p)` — the flag.

## The encoding playbook

1. The charset — `+/=`/hex/`01`/`.-`/`ADFGVX`.
2. `enc_detect`/`other-ciphers` — the decode.
3. `cipher_id` on the output if a `ct` remains.

## The verify

`pt` language + `enc(pt)=ct` — `verify*.md`.
