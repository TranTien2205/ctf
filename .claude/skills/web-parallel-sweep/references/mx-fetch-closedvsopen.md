# Cell: fetch / closed-vs-open

Method module for `web-parallel-sweep`. The sweep splits a web target by bug-class family into bounded measurements; this file is one named piece of that method. Ten families reporting is not ten families closed.

How the `fetch` family answers `closed-vs-open`.

## Read

The family's brief and contract fields that answer this question -
which probe order applies, what its return looks like, how its
closed-vs-open disposition is read, and when it parks instead of
probing.

## Guard

The answer must come from the brief and the returned JSON - an
agent's prose about it is a claim, not a measurement.
