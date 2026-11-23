# Service recon: customtcp

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Unknown TCP service: connect, wait for banner
(text prompt or binary), send newline then HELP then a random
token - responses reveal the protocol family. A text command
interface ('Enter name:', '> ') = interactive service ->
pwn-binary-triage or the rev depth. Binary protocol bytes go
verbatim into the observation for analysis.
## Pivot

Signal harvested -> out-*; route named -> that skill.
