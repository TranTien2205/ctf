# Invalid curve — reference card

**Applies when:** a service computes `d·P` on a supplied point without an
on-curve check.

**Tool:** `tools/crypto/ec.py` (point arithmetic on custom curves) + `bsgs`/
`pohlig-hellman` for the small dlogs.

**Preconditions:** server skips validation; enough smooth-order fake curves
to cover `n` via CRT.

**Falsifier:** validation error on submission → impossible.

**Verify:** `d·G == Q` on the real curve.

**Deep:** `invalid-curve-deep.md`.
