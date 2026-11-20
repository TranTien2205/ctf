# an xor layer of uuencode

**Carrier:** uuencode — begin + M... lines.

**Layer:** an xor layer — a keyed xor.

Run the standard decoder for the carrier first; a clean decode closes it, a fail peels the next layer.
