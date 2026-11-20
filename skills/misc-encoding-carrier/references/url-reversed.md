# reversed of url-encoding

**Carrier:** url-encoding — %XX escapes.

**Layer:** reversed — the blob backwards.

Run the standard decoder for the carrier first; a clean decode closes it, a fail peels the next layer.
