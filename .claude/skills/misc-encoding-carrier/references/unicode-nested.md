# nested layers of unicode escapes

**Carrier:** unicode escapes — \uXXXX \xXX.

**Layer:** nested layers — a decode chain.

Run the standard decoder for the carrier first; a clean decode closes it, a fail peels the next layer.
