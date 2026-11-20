# big numbers in CAPTCHA-ish parsing

**Puzzle:** CAPTCHA-ish parsing — ASCII art -> text.

**Edge:** big numbers — overflow past int64.

A solver that passes early rounds still fails here — log raw bytes to catch the drift.
