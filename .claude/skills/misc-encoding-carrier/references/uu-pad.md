# a padded layer of uuencode

**Carrier:** uuencode — begin + M... lines.

**Layer:** a padded layer — a wrapper around.

Run the standard decoder for the carrier first; a clean decode closes it, a fail peels the next layer.
