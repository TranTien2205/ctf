# Decode TWICE — the standard trick

`base64(hex(...))` — the standard trick is layered encodings; decode
until the output is plain text or a layer fails.

## The layers

Decode until plain text or a layer fails — not once.

## The standard trick

base64(hex(...)) — decode twice, minimum.
