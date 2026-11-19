# Edge cases variant — the boundary shapes restated

## The signature edges

- DER-encoded `(r,s)` → extract the two INTEGERs.
- `s` high/low form — `s` or `n-s` both verify; attack works either way.
- `r`,`s` as hex strings, ints, or DER — normalize before `--sigs`.
- `z` as message text → hash first.
- `z` as `{"r","s","h"}` — wrong key name — use `{"r","s","z"}`.

## The count edges

- Mixed reuse+bias — split the reuse pair to `ecdsa-nonce-reuse`, the rest
  to `hnp-ecdsa`.
- `m` just under `required_signatures` — gather one more.
- `m` way over — prune; LLL is `O(m+1)` dims in pure python.

## The curve edges

- `p` vs `n` swapped — `order` is `n`.
- `G` not standard — verify `n·G == ∞` to confirm.
- `Q` compressed — decompress via `y² = x³+ax+b` root.

## The tool edges

- `--sigs` is a file — inline JSON rejected.
- `--nonce-bound` = integer `B`; `--nonce-bits` = `log2(B)`.
- `lll.py` pure-python — `m > 40` dims is slow.
- `bsgs max_table = 1<<22` default — raise in code for bigger bounds.

## The verify edges

- `d` on the wrong curve — verify against the *supplied* params.
- `h ∉ <g>` — `pow(h, ord, p) == 1` precheck.
