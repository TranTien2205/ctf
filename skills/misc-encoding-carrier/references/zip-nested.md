# nested layers of zip

**Carrier:** zip — PK\x03\x04 magic.

**Layer:** nested layers — a decode chain.

Run the standard decoder for the carrier first; a clean decode closes it, a fail peels the next layer.
