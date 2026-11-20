# stripped bytes of base64

**Carrier:** base64 — alphabet 64, = padding, len%4==0.

**Layer:** stripped bytes — bytes removed.

Run the standard decoder for the carrier first; a clean decode closes it, a fail peels the next layer.
