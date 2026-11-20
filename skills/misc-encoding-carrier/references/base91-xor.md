# an xor layer of base91

**Carrier:** base91 — no padding, broad set.

**Layer:** an xor layer — a keyed xor.

Run the standard decoder for the carrier first; a clean decode closes it, a fail peels the next layer.
