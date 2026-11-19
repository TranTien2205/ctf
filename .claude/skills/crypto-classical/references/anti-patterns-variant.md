# Anti-patterns variant — the habits, by family

## The `caesar` anti-patterns

- **Annealing a Caesar** — `subst` on a `k`-shift — `caesar` (25 `k`) is
  faster; the chi² min is `k`.
- **A keyed alphabet as a `k`** — `subst` on the `k`-shifted output — a
  `KEYWORD`-alphabet `+k` is a `σ`, not a `k`.
- **A `k=0` read as a cipher** — `c=p` — `cipher_id` says "not a cipher" —
  the `ct` is the answer.

## The `subst` anti-patterns

- **Annealing a polyalpha** — `subst` on a `vigenere` (IC~0.038) — the
  anneal can't crack it — `cipher_id` first.
- **A near-decode as the flag** — `gLAG{` — the `flag{` positions pin `σ` —
  swap and re-score.
- **Re-running a falsified `σ`** — the anneal plateaus → `π`/other — the
  falsifier is a signal.

## The `vigenere` anti-patterns

- **The `L` mis-estimate** — `L'=k·L` gives a near-decode — try `L`/`L/2`/`2L`.
- **A Beaufort as a Vigenere** — `c=k-p` not `c=p+k` — try `p=k-c`.
- **An autokey as a Vigenere** — `key=primer+pt` — no periodic `L` — a crib.
- **A running-key as a Vigenere** — a long `key` — a crib/the key text.

## The `railfence`/`π` anti-patterns

- **A `σ` as a `π`** — `subst` on a scrambled `ct` fails — `π` first —
  `π(σ(p))`.
- **A columnar as a rail-fence** — `w` columns, not `r` rails — brute `w`.
- **The `n` not a grid** — `n` prime → a `σ`/`k`, not a `π`.

## The boundary anti-patterns

- **An encoding as a cipher** — `enc_detect` first — the charset is the tell.
- **A layered re-attack** — `cipher_id` on the *output*, not a re-run.
- **A named cipher as a `classical_solve`** — `other-ciphers*.md` → a script.
