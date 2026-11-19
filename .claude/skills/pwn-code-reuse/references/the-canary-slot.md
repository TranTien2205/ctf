# Placing the canary — the leak's slot


If a canary exists: the leaked value goes at canary_offset in the
padding — the chain continues past it.

## The layout

    [padding to canary] [canary] [pad to rip] [chain]

## Falsifier

The canary isn't leaked: the overwrite aborts at the check — a leak
is the prerequisite.
