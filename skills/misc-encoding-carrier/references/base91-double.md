# a double layer of base91

**Carrier:** base91 — no padding, broad set.

**Layer:** a double layer — decode twice.

Run the standard decoder for the carrier first; a clean decode closes it, a fail peels the next layer.
