# a double layer of unicode escapes

**Carrier:** unicode escapes — \uXXXX \xXX.

**Layer:** a double layer — decode twice.

Run the standard decoder for the carrier first; a clean decode closes it, a fail peels the next layer.
