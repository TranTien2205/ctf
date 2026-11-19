# Remote vs local — socket protocol vs process — checklist

Remote pwn is a socket conversation: read the prompt, send the payload, read the response. The discipline is netcat/python-socket, not pwntools here.

## Checklist

- [ ] nc <host> <port> — read the protocol first (banner, prompt, expected format).
- [ ] Send the cyclic to find the offset remotely — the fault comes back as a disconnect or error.
- [ ] Send the payload as raw bytes + newline; read the flag from the response.
- [ ] For scripted sends, python socket (stdlib) or a heredoc into nc — not pwntools.

## Abort conditions

- Forking servers give a fresh canary/ASLR per connection ONLY if exec'd; forked children share it.
- Send the payload bytes then a newline — some reads block until the newline.
- Raw socket with `python3 -c` or `nc` heredoc works; pwntools is absent here.

## Falsifier

Falsifier — the remote service doesn't fork per connection and one crash kills it for everyone: exploit carefully — every probe is shared state.
