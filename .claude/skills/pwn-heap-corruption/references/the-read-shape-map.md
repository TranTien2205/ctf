# Read shapes — what the leak channel returns — map

Companion to `the-read-shape.md`.

| Channel | Returns |
|---|---|
| show on dangling | the chunk's user bytes (bin links) |
| a stale uninit read | previous user's data |
| an error message | fixed format — rarely controlled |
| a side channel | timing/behavior bits |
