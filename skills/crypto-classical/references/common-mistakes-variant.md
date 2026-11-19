# Common mistakes variant — the errors, by family

## The `caesar` mistakes

- **`subst` on a Caesar** — the chi² min is `k` — `caesar` first.
- **A keyed alphabet as a `k`** — `subst` on the output — a `σ`.
- **A `k=0` read as a cipher** — `cipher_id` "not a cipher" — the `ct` is the
  answer.

## The `subst` mistakes

- **`subst` on a `vigenere`** — IC~0.038 — the anneal fails — `cipher_id`
  first.
- **`gLAG{` as the flag** — polish the `σ` — `σ⁻¹(g)=f`.
- **Re-running a falsified `σ`** — the anneal plateaus → `π`.

## The `vigenere` mistakes

- **The `L` mis-estimate** — `L`/`L/2`/`2L`.
- **A Beaufort as a Vigenere** — `p=k-c`.
- **An autokey as a Vigenere** — `key=primer+pt`.
- **A running-key as a Vigenere** — a crib.

## The `railfence`/`π` mistakes

- **`subst` on a `π(σ(p))`** — `π` first (position-only), then `subst`.
- **A columnar as a rail-fence** — brute `w`, not `r`.
- **`n` prime read as a grid** — `σ`/`k`, not `π`.

## The boundary mistakes

- **`+/=`/hex/`01` as a cipher** — `enc_detect`.
- **`cipher_id` on the same `ct`** — a layered `ct` — on the output.
- **A named cipher in `classical_solve`** — `other-ciphers*.md` → a script.
- **The stats over the format** — a short `ct` — `flag{` positions carry.
