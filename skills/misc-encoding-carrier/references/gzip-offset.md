# an offset layer of gzip

**Carrier:** gzip — \x1f\x8b magic.

**Layer:** an offset layer — shifted bytes.

Run the standard decoder for the carrier first; a clean decode closes it, a fail peels the next layer.
