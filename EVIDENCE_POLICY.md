# Evidence Policy

Every exploit claim has two separate fields: `claim` and `evidence`.

- Source evidence identifies the exact file, line, route, input, and sink.
- Probe evidence records the exact command/request, timestamp, status, and
  bounded output or callback observation.
- Verification evidence is the actual flag-bearing HTTP response or supplied
  artifact read during this session.
- A writeup, source literal, guessed flag, timeout, or tool-generated label is
  not live verification.

Cards must use `quality.verified_live: false` unless the verification evidence
is present. Unknown metadata stays `null` or `unknown`; validators and critics
must reject unsupported additions.
