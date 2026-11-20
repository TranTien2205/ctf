# an offset layer of url-encoding

**Carrier:** url-encoding — %XX escapes.

**Layer:** an offset layer — shifted bytes.

Run the standard decoder for the carrier first; a clean decode closes it, a fail peels the next layer.
