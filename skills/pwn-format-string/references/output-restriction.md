# Output restriction — the filtered/truncated leak


The service may filter or truncate the format's output: the %p run's
words are cut, or the output is cleaned — the leak is partial.

## Shapes

- The output is capped → truncated leak.
- A sanitizer strips %/hex → filtered.
- Only some args reachable → partial leak.

## Steps

1. If truncated: the leak is partial — the %n write doesn't care.
2. If sanitized: the write still works blind.
3. Check which arg positions are reachable.

## Falsifier

The output is fully suppressed AND no oracle exists: the read can't be
harvested; only a blind write remains.
