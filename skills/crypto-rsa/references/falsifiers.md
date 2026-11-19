# Falsifiers — what closes each attack

- `gcd(ni,nj)=1` all → `batch-gcd` dead.
- `gcd(e1,e2)>1` → `common-modulus` dead.
- `a` budget out, `a²-n` never square → `fermat` dead.
- `d≥n^0.25` → `wiener`; `d≥n^0.292` → `wiener`+`boneh-durfee`.
- window `<n^0.25` / `<n^(1/e)` → `coppersmith`.
- `m^e≥n` → `small-e-root`/`nth-root`.
- `<e` n's / `∏n<m^e` / a pad → `hastad`.
- `gcd(a^{B!}-1,n)=1` at `B` → `pollard-pm1`.
- relation not linear → `franklin-reiter`.
- `∏pi≤m` / no fault / inconsistent `dp` → `crt`.
- `gcd(e,phi)=1` → `eth-root` — normal `inverse`.
- `d`/`phi` fails `pow` → `factor-from-d`/`rsa-decrypt` wrong input.
- every bound met → the class falsifier → `class-boundary.md`.

See `falsifier-map.md`, `per-falsifier.md`, `negative-map.md`.
