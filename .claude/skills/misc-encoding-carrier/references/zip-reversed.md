# reversed of zip

**Carrier:** zip — PK\x03\x04 magic.

**Layer:** reversed — the blob backwards.

Run the standard decoder for the carrier first; a clean decode closes it, a fail peels the next layer.
