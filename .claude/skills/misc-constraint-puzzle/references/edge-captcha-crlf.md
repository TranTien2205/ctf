# CRLF vs LF in CAPTCHA-ish parsing

**Puzzle:** CAPTCHA-ish parsing — ASCII art -> text.

**Edge:** CRLF vs LF — the wire's line ending.

A solver that passes early rounds still fails here — log raw bytes to catch the drift.
