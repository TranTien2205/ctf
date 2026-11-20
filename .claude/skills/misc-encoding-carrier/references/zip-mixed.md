# mixed carriers of zip

**Carrier:** zip — PK\x03\x04 magic.

**Layer:** mixed carriers — different layers.

Run the standard decoder for the carrier first; a clean decode closes it, a fail peels the next layer.
