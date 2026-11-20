# a single layer of base32

**Carrier:** base32 — A-Z2-7, = padding in 8s.

**Layer:** a single layer — one decode.

Run the standard decoder for the carrier first; a clean decode closes it, a fail peels the next layer.
