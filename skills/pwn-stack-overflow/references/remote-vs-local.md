# Remote vs local — socket protocol vs process

Remote pwn is a socket conversation: read the prompt, send the payload, read the response. The discipline is netcat/python-socket, not pwntools here.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| nc <host> <port> gives a prompt | remote service | socket loop |
| the service echoes/forks per connection | remote semantics | fresh state per conn |
| a banner + a read prompt | the input point | send the payload |

## Steps

1. nc <host> <port> — read the protocol first (banner, prompt, expected format).
2. Send the cyclic to find the offset remotely — the fault comes back as a disconnect or error.
3. Send the payload as raw bytes + newline; read the flag from the response.
4. For scripted sends, python socket (stdlib) or a heredoc into nc — not pwntools.

## Falsifier

Falsifier — the remote service doesn't fork per connection and one crash kills it for everyone: exploit carefully — every probe is shared state.

## Traps

- Forking servers give a fresh canary/ASLR per connection ONLY if exec'd; forked children share it.
- Send the payload bytes then a newline — some reads block until the newline.
- Raw socket with `python3 -c` or `nc` heredoc works; pwntools is absent here.

## Commands

```bash
nc <host> <port>
python3 -c "import socket;s=socket.socket();s.connect(('<h>',<p>));s.send(b'A'*40);print(s.recv(1024))"
```

## Cross-references

`sendline-protocols.md` · `canary-bypass.md`
