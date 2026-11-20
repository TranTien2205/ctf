# a single layer of base85/z85

**Carrier:** base85/z85 — no padding, wider set.

**Layer:** a single layer — one decode.

Run the standard decoder for the carrier first; a clean decode closes it, a fail peels the next layer.
