# non-ASCII bytes in CAPTCHA-ish parsing

**Puzzle:** CAPTCHA-ish parsing — ASCII art -> text.

**Edge:** non-ASCII bytes — a round with utf8/wide chars.

A solver that passes early rounds still fails here — log raw bytes to catch the drift.
