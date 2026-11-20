# non-ASCII bytes in a maze

**Puzzle:** a maze — grid walking, path output.

**Edge:** non-ASCII bytes — a round with utf8/wide chars.

A solver that passes early rounds still fails here — log raw bytes to catch the drift.
