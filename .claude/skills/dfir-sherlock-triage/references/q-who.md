# Question type: who

Routing module for `dfir-sherlock-triage`. Question text +
artifact inventory -> one depth file. The router never answers
the question; it names who does.

Logon/session artifacts: Security.evtx 4624/4625,
auth.log, wtmp - authentication-trace.

## Pivot

Question literal -> its q-* module; artifact absent -> fal-*.
