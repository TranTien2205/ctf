# Bracket first — wc and head/tail

    wc -l access.log
    head -1 access.log; tail -1 access.log

Line count + first/last timestamps = the volume and the window.
Every "the anomalous IP hit 3000 times" claim needs this
denominator to mean anything.

## What it tells you

- Volume — is this a 500-line log or a 5-million-line one (the
  method scales).
- The timeframe — the window the "when" answer must sit inside.
- The timestamp format — which leads to the timezone question.
