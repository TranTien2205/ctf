# Round state — N matters

Some services ask `round N` and expect the Nth answer — track the
round counter from the prompt, not a local counter; a dropped round
desyncs a local one.

## The counter

Track N from the prompt, not a local counter.
