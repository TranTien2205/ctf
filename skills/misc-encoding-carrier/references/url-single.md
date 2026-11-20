# a single layer of url-encoding

**Carrier:** url-encoding — %XX escapes.

**Layer:** a single layer — one decode.

Run the standard decoder for the carrier first; a clean decode closes it, a fail peels the next layer.
