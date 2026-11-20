# stripped bytes of gzip

**Carrier:** gzip — \x1f\x8b magic.

**Layer:** stripped bytes — bytes removed.

Run the standard decoder for the carrier first; a clean decode closes it, a fail peels the next layer.
