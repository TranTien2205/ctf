# nested layers of gzip

**Carrier:** gzip — \x1f\x8b magic.

**Layer:** nested layers — a decode chain.

Run the standard decoder for the carrier first; a clean decode closes it, a fail peels the next layer.
