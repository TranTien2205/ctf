# tools/forensics/hive_parse.py

Routing module for `dfir-sherlock-triage`. Question text +
artifact inventory -> one depth file. The router never answers
the question; it names who does.

Offline registry reads - keys, values, last-write
times for persistence and user-activity questions.

## Pivot

Question literal -> its q-* module; artifact absent -> fal-*.
