# reversed of gzip

**Carrier:** gzip — \x1f\x8b magic.

**Layer:** reversed — the blob backwards.

Run the standard decoder for the carrier first; a clean decode closes it, a fail peels the next layer.
