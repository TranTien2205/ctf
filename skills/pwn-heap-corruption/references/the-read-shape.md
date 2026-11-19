# Read shapes — what the leak channel returns


| Channel | Returns |
|---|---|
| show on dangling | the chunk's user bytes (bin links) |
| a stale uninit read | previous user's data |
| an error message | fixed format — rarely controlled |
| a side channel | timing/behavior bits |

The leak's shape decides what it can disclose — links (addresses) vs
data (content).
