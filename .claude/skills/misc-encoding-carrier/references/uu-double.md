# a double layer of uuencode

**Carrier:** uuencode — begin + M... lines.

**Layer:** a double layer — decode twice.

Run the standard decoder for the carrier first; a clean decode closes it, a fail peels the next layer.
