# Two questions in one read

A fast server writes two rounds back-to-back — the leftover after
the first terminator is the next question's head. The buffer keeps
it; a fresh recv() would block forever.

## Leftover

The buffer keeps the next question's head.

## Leftover

The buffer keeps the next head.
