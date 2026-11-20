# nested layers of quoted-printable

**Carrier:** quoted-printable — =XX escapes.

**Layer:** nested layers — a decode chain.

Run the standard decoder for the carrier first; a clean decode closes it, a fail peels the next layer.
