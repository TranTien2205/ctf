# an offset layer of uuencode

**Carrier:** uuencode — begin + M... lines.

**Layer:** an offset layer — shifted bytes.

Run the standard decoder for the carrier first; a clean decode closes it, a fail peels the next layer.
