# Read shapes — what the leak channel returns — checklist

Companion to `the-read-shape.md`.

## Checklist

- [ ] Channel | Returns
- [ ] show on dangling | the chunk's user bytes (bin links)
- [ ] a stale uninit read | previous user's data
- [ ] an error message | fixed format — rarely controlled
- [ ] a side channel | timing/behavior bits
