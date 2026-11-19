# The real bound — what actually limits the fmtstr


The input's real limit: the read's bound, a format-length cap, or the
output buffer — the payload must fit whichever binds first.

## Bounds

- input length cap — short fmtstr — positional args help.
- output capped — truncated leak — the write unaffected.
- a size arg — the bound — the limit.

## Falsifier

The fmtstr can't fit the needed specifiers in the bound: express only
what fits or split across calls.
