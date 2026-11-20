# mixed carriers of gzip

**Carrier:** gzip — \x1f\x8b magic.

**Layer:** mixed carriers — different layers.

Run the standard decoder for the carrier first; a clean decode closes it, a fail peels the next layer.
