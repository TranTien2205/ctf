# nested layers of base32

**Carrier:** base32 — A-Z2-7, = padding in 8s.

**Layer:** nested layers — a decode chain.

Run the standard decoder for the carrier first; a clean decode closes it, a fail peels the next layer.
