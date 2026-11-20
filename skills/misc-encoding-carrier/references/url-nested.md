# nested layers of url-encoding

**Carrier:** url-encoding — %XX escapes.

**Layer:** nested layers — a decode chain.

Run the standard decoder for the carrier first; a clean decode closes it, a fail peels the next layer.
