# nested layers of base85/z85

**Carrier:** base85/z85 — no padding, wider set.

**Layer:** nested layers — a decode chain.

Run the standard decoder for the carrier first; a clean decode closes it, a fail peels the next layer.
