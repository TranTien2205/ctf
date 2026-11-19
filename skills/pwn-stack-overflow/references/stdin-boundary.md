# Stdin boundary — the read's actual stop condition


fgets stops at newline or n-1; read stops at n; scanf %s stops at
whitespace; readline at newline. The payload's last byte depends on the
read's terminator.

## The matrix

| Read | Stops at | Banned in payload |
|---|---|---|
| `read(fd,buf,n)` | n bytes | none (raw) |
| `fgets(buf,n)` | newline or n-1 | 
 splits it |
| `scanf %s` | whitespace |  	
 |
| `gets` | newline | 
 splits it |
| `readline` | newline | 
 splits it |
| `memcpy(dst,src,n)` | n bytes | none |

## The rule

Send payload + the terminator; a banned byte inside the payload truncates
the input before the terminator.
