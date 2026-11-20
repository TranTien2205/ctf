# trailing newline in CAPTCHA-ish parsing

**Puzzle:** CAPTCHA-ish parsing — ASCII art -> text.

**Edge:** trailing newline — send must/must-not end with \n.

A solver that passes early rounds still fails here — log raw bytes to catch the drift.
