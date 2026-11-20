# whitespace variance in CAPTCHA-ish parsing

**Puzzle:** CAPTCHA-ish parsing — ASCII art -> text.

**Edge:** whitespace variance — spaces vs tabs vs none.

A solver that passes early rounds still fails here — log raw bytes to catch the drift.
