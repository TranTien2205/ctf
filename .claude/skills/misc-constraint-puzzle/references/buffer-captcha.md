# buffer the stream for CAPTCHA-ish parsing

**Step:** buffer the stream — recv until the terminator, not one read.

**Puzzle:** CAPTCHA-ish parsing — ASCII art -> text.

Build the step against the CAPTURED transcript, not a guess; log the raw bytes per round.
