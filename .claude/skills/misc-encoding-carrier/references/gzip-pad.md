# a padded layer of gzip

**Carrier:** gzip — \x1f\x8b magic.

**Layer:** a padded layer — a wrapper around.

Run the standard decoder for the carrier first; a clean decode closes it, a fail peels the next layer.
