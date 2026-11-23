# Worked example: hostport-raw

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Walked: supplied <host>:31337, no scheme.

1. GET http://<host>:31337 -> connection resets: not HTTP.
2. nc <host> 31337 -> banner 'Welcome! Send me bytes:' ->
   interactive text service (svc-customtcp).
3. newline probe -> 'ERROR: unknown' -> command-style service.
4. 'HELP' -> 'commands: READ, WRITE, EXIT' -> the protocol's
   verbs enumerated in one request.
5. Observations: text protocol, verbs READ/WRITE, no auth
   prompt, CTF-instance shape.
6. Route: pwn-binary-triage or the custom-protocol depth -
   recon hands the verb list + verbatim prompt.
## Pivot

Signal harvested -> out-*; route named -> that skill.
