# a double layer of zip

**Carrier:** zip — PK\x03\x04 magic.

**Layer:** a double layer — decode twice.

Run the standard decoder for the carrier first; a clean decode closes it, a fail peels the next layer.
