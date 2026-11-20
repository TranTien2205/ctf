# a padded layer of base64

**Carrier:** base64 — alphabet 64, = padding, len%4==0.

**Layer:** a padded layer — a wrapper around.

Run the standard decoder for the carrier first; a clean decode closes it, a fail peels the next layer.
