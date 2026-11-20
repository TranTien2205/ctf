# nested layers of uuencode

**Carrier:** uuencode — begin + M... lines.

**Layer:** nested layers — a decode chain.

Run the standard decoder for the carrier first; a clean decode closes it, a fail peels the next layer.
