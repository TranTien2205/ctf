# nested layers of base64

**Carrier:** base64 — alphabet 64, = padding, len%4==0.

**Layer:** nested layers — a decode chain.

Run the standard decoder for the carrier first; a clean decode closes it, a fail peels the next layer.
