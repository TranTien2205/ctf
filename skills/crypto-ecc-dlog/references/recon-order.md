# Recon order — the read before the probes

## Recon 1 — what kind of artifact

- a JSON/text handout → parse `p, a, b, G, n, (r,s)` fields.
- a signing service → probe `sign(m)` on two inputs to see if `(r,s)` changes.
- a DH/point oracle → submit `(x, y)` to see if it validates.

## Recon 2 — the group identity

- Named curve → known `n`, `G`, `p` — bug is in the nonce or the use.
- Custom `p, a, b` → defect hunting — `Δ`, `#E`, `ord` smoothness.
- `h = g^x mod p` → `p-1`/`ord(g)` smoothness.

## Recon 3 — the signature inventory

- Count sigs; dedupe `r`; compute `z` per message (FIPS truncation first).
- Check `len(sigs) ≥ required_signatures(order_bits, nonce_bits)` for HNP.

## Recon 4 — the deliverable

A `d`/`x` that verifies, or a `d` that forges/decrypts into `flag{…}`.
Plan the end: what does the recovered scalar *buy*?

## The tools needed

`crypto_attack.py` (all attack ids) + `tools/crypto/{ec,dlog,hnp,smart_attack,singular_ec,lll,numtheory}.py`. `selftest` each once to confirm availability:

```bash
# runnable standalone selftests:
python3 tools/crypto/smart_attack.py --selftest
python3 tools/crypto/singular_ec.py --selftest
# the library modules (ec/dlog/hnp/lll/numtheory) have no __main__ — import check:
python3 -c "from tools.crypto import ec, dlog, hnp, lll, numtheory" 
```
