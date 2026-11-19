# The edit op — the corruption channel


edit(i, data) writes ptr[i]'s contents — on a freed slot it writes the
bin metadata: fd poison in one op.

## Use

- edit on a tcache chunk → set fd = (pos>>12)^target — the poison.
- edit on an unsorted chunk → corrupt its fd/bk — bin-link write.
- edit on a live object → normal data write.

## Falsifier

edit bounds-checks liveness (refuses freed slots): corruption needs an
overflow shape instead.
