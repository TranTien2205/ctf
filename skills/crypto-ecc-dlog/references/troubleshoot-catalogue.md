# Troubleshoot catalogue — failure → cause → fix

## The `crypto_attack.py` errors

| Error | Cause | Fix |
|---|---|---|
| `supply --sigs FILE.json` | inline JSON passed | write to file |
| `need(data, "order")` | `--order` missing | add `--order n` |
| JSON parse error | wrong `--sigs` format | `[r,s,z]` or `{"r","s","z"}` |
| `ValueError` on `--nonce-*` | bound as string | pass integer `B` |

## The math failures

| Symptom | Cause | Fix |
|---|---|---|
| `d` plausible, verify fails | `z` convention | truncation vs `mod n` |
| `hnp-ecdsa` no `d` | count/bound | `required_signatures`, widen `B` |
| `pohlig-hellman` stalls | largest factor > 2⁴⁰ | `bsgs` or defect route |
| `bsgs` no collision | bound/order wrong | `h ∈ <g>` check, `ord` recheck |
| `smart` fails | `#E ≠ p` | `smoothness #E` → PH |
| `singular` fails | `Δ ≠ 0` | not singular |
| invalid curve rejected | server validates | impossible |

## The format failures

| Symptom | Cause | Fix |
|---|---|---|
| `--sigs` parse error | `h` not `z` key | use `{"r","s","z"}` |
| DER sig fails | raw DER bytes | extract `(r,s)` ints first |
| compressed `Q` verify fails | not decompressed | `y² = x³+ax+b` root |
| hex vs int mismatch | mixed formats | normalize to int |

## The route failures

| Symptom | Cause | Fix |
|---|---|---|
| nothing works | wrong class | `crypto-triage` re-route |
| math clean, no flag | `x`/`d` isn't the flag | decrypt/forge step pending |
