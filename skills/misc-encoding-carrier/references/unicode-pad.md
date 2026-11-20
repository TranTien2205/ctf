# a padded layer of unicode escapes

**Carrier:** unicode escapes — \uXXXX \xXX.

**Layer:** a padded layer — a wrapper around.

Run the standard decoder for the carrier first; a clean decode closes it, a fail peels the next layer.
