# a single layer of unicode escapes

**Carrier:** unicode escapes — \uXXXX \xXX.

**Layer:** a single layer — one decode.

Run the standard decoder for the carrier first; a clean decode closes it, a fail peels the next layer.
