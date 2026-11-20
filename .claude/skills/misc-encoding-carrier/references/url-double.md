# a double layer of url-encoding

**Carrier:** url-encoding — %XX escapes.

**Layer:** a double layer — decode twice.

Run the standard decoder for the carrier first; a clean decode closes it, a fail peels the next layer.
