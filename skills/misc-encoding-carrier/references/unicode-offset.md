# an offset layer of unicode escapes

**Carrier:** unicode escapes — \uXXXX \xXX.

**Layer:** an offset layer — shifted bytes.

Run the standard decoder for the carrier first; a clean decode closes it, a fail peels the next layer.
