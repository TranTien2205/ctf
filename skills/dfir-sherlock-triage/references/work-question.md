# Read the question literally

Routing module for `dfir-sherlock-triage`. Question text +
artifact inventory -> one depth file. The router never answers
the question; it names who does.

Investigation questions are literal: 'when did X run' wants
a timestamp, 'what did X take' wants a data path. The
literal ask names the artifact and the depth file.

## Pivot

Question literal -> its q-* module; artifact absent -> fal-*.
