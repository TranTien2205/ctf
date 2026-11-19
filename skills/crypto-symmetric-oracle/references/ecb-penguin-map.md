# The ECB-penguin intuition — structure survives encryption — map

| Structure you control | Attack |
|---|---|
| A repeated block at a chosen offset | byte-at-a-time (make the secret byte share your block) |
| A whole block's value | cut-and-paste (splice it) |
| Block boundaries themselves | reordering (move fields) |

Expanded rows and abort conditions: `ecb-penguin.md` and `ecb-penguin-deep.md`.
