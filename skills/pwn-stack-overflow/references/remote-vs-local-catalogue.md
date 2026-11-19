# Remote vs local — socket protocol vs process — case catalogue

Remote pwn is a socket conversation: read the prompt, send the payload, read the response. The discipline is netcat/python-socket, not pwntools here.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | nc <host> <port> gives a prompt | remote service | socket loop |
| 2 | the service echoes/forks per connection | remote semantics | fresh state per conn |
| 3 | a banner + a read prompt | the input point | send the payload |

## Falsifier

Falsifier — the remote service doesn't fork per connection and one crash kills it for everyone: exploit carefully — every probe is shared state.
