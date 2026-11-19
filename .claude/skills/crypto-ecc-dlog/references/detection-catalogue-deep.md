# Detection catalogue deep — every signal expanded

## The signature signals, expanded

### The `r` signal

`r` is `x(k·G) mod n` — identical `r` means identical `k`. The single
most valuable read: `Counter(r)` on the sig list. A duplicate pair routes
to `ecdsa-nonce-reuse` — closed form, no lattice.

### The `k` bound signal

The challenge says "128-bit nonce", "timestamp k", "8-bit leak" — or you
infer it from observed `k` magnitudes on an oracle. `k < B` uniform →
`hnp-ecdsa`; partial bits → `hnp`.

### The sig-count signal

`required_signatures(order_bits, nonce_bits)` decides whether you have
enough to even run the lattice — gather to the count, not past it.

## The dlog signals, expanded

### The order signal

`ord(g)` — `p-1` for a generator, else a factor. `smoothness --n ord` is
the gate; the largest prime factor decides PH feasibility.

### The bound signal

`x < B` stated → `bsgs --order B`; `x` unstated + `ord` small → `bsgs`;
else defect or protocol.

### The subgroup signal

`pow(h, ord(g), p) == 1` — `h ∈ <g>` or the solve targets `ord(h)`.

## The defect signals, expanded

### The `Δ` signal

`Δ = -16(4a³+27b²) mod p` — exactly `0` → singular.

### The `#E` signal

`#E` == `p` → anomalous; smooth → PH; prime → generic-hard.

### The validation signal

Does the server check `y² == x³+ax+b` on submitted points? No → invalid
curve; yes → closed.

## The format signals, expanded

- DER-encoded sig → extract `(r,s)` ints first.
- Compressed `Q` (`02/03||x`) → decompress.
- `z` as hex → `--sigs` accepts it; must be truncated hash.
