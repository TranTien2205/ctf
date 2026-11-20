# a padded layer of quoted-printable

**Carrier:** quoted-printable — =XX escapes.

**Layer:** a padded layer — a wrapper around.

Run the standard decoder for the carrier first; a clean decode closes it, a fail peels the next layer.
