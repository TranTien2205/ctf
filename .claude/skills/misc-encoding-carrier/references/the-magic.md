# Magic bytes — a container not an encoding

`\x1f\x8b` gzip, `PK\x03\x04` zip, `\x89PNG` image — a blob that
opens with magic bytes is a file, not an encoding; route it to the
right class.

## A file

Magic bytes = a container, not an encoding.

## Route out

A container routes to its own class.
