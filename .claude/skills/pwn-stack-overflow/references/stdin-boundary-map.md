# Stdin boundary — the read's actual stop condition — map

Companion to `stdin-boundary.md`.

## The matrix
| Read | Stops at | Banned in payload |
|---|---|---|
| `read(fd,buf,n)` | n bytes | none (raw) |
| `fgets(buf,n)` | newline or n-1 | 
| `scanf %s` | whitespace |  	
| `gets` | newline | 
| `readline` | newline | 
| `memcpy(dst,src,n)` | n bytes | none |
## The rule
