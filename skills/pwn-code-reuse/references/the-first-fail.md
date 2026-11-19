# The first failure — bisecting the chain


A chain that doesn't work: bisect — verify the first gadget landed,
then the second, then the call.

## The method

- Break at the overwrite point; step.
- If gadget 1 doesn't execute: the overwrite missed — re-measure the
  offset.
- If gadget N misbehaves: its side effects — audit the tail.
- If the call crashes: alignment or a bad target.
