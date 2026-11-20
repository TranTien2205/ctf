# a double layer of gzip

**Carrier:** gzip — \x1f\x8b magic.

**Layer:** a double layer — decode twice.

Run the standard decoder for the carrier first; a clean decode closes it, a fail peels the next layer.
