# Detection — when this class applies

A log file (or set) is the handout and the question is a fact
inside — an IP, a user, a request, a moment.

## Signals

- access.log / auth.log / syslog / app log / EVTX as the artifact.
- The question is extractive: "which IP", "what time", "who",
  "what command".
- The answer is a log line + the anomaly that names it.
- Confusable: dfir-authentication-trace (auth-specific),
  forensics-pcap-carve (a pcap).
