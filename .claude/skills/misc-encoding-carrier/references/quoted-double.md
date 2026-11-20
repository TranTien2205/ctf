# a double layer of quoted-printable

**Carrier:** quoted-printable — =XX escapes.

**Layer:** a double layer — decode twice.

Run the standard decoder for the carrier first; a clean decode closes it, a fail peels the next layer.
