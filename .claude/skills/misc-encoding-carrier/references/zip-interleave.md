# interleaved of zip

**Carrier:** zip — PK\x03\x04 magic.

**Layer:** interleaved — two channels woven.

Run the standard decoder for the carrier first; a clean decode closes it, a fail peels the next layer.
