# a single layer of quoted-printable

**Carrier:** quoted-printable — =XX escapes.

**Layer:** a single layer — one decode.

Run the standard decoder for the carrier first; a clean decode closes it, a fail peels the next layer.
