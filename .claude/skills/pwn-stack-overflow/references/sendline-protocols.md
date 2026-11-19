# The sendline protocol — remote service shape

A remote pwn service reads a line, processes it, responds. The payload must survive the transport: newlines, length limits, and the service's framing.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| nc gives a prompt then reads | line-oriented | send + newline |
| binary protocol with a length field | framed | length prefix matters |
| the service echoes the input | echo oracle | verify bytes landed |

## Steps

1. nc <host> <port> — read the banner/prompt first.
2. Send payload + '\n' — most reads want the newline.
3. For binary protocols: the length field may bound your input.
4. Read the response; the flag or the crash is the answer.

## Falsifier

Falsifier — the service's read bound stops before your offset: the payload can't reach the saved state at this size.

## Traps

- A length-prefixed protocol bounds the payload — the offset must fit inside it.
- Newline-terminated reads need the trailing '\n'.
- Some services read a fixed number of bytes regardless of newlines — send exactly that many.

## Commands

```bash
nc <host> <port>
python3 -c "import socket;s=socket.socket();s.connect(('<h>',<p>));s.send(b'...')"   # stdlib socket
```

## Cross-references

`remote-vs-local.md`
