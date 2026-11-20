# non-ASCII bytes in small crypto

**Puzzle:** small crypto — hash per round, nonce find.

**Edge:** non-ASCII bytes — a round with utf8/wide chars.

A solver that passes early rounds still fails here — log raw bytes to catch the drift.
