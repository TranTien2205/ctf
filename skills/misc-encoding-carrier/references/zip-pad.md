# a padded layer of zip

**Carrier:** zip — PK\x03\x04 magic.

**Layer:** a padded layer — a wrapper around.

Run the standard decoder for the carrier first; a clean decode closes it, a fail peels the next layer.
