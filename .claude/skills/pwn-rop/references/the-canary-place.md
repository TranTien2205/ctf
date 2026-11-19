# Placing the canary — the protected overwrite


With a canary present, the leaked canary goes at its exact slot —
the chain continues past it:

    [pad to canary] [canary] [pad to rip] [chain]

## The leak

The canary's value comes from a prior leak — fmtstr, an info
disclosure, a fork-server oracle — measured, not guessed.

## Falsifier

No canary leak channel: the overwrite aborts; a different entry
primitive is needed.
