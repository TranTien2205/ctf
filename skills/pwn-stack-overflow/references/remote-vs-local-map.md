# Remote vs local — socket protocol vs process — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| nc <host> <port> gives a prompt | remote service | socket loop |
| the service echoes/forks per connection | remote semantics | fresh state per conn |
| a banner + a read prompt | the input point | send the payload |

## Falsifier

Falsifier — the remote service doesn't fork per connection and one crash kills it for everyone: exploit carefully — every probe is shared state.
