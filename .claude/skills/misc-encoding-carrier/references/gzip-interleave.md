# interleaved of gzip

**Carrier:** gzip — \x1f\x8b magic.

**Layer:** interleaved — two channels woven.

Run the standard decoder for the carrier first; a clean decode closes it, a fail peels the next layer.
