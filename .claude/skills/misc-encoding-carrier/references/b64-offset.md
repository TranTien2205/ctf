# an offset layer of base64

**Carrier:** base64 — alphabet 64, = padding, len%4==0.

**Layer:** an offset layer — shifted bytes.

Run the standard decoder for the carrier first; a clean decode closes it, a fail peels the next layer.
