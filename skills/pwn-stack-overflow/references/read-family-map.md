# The read-family matrix — which input function and what it allows — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| gets()/scanf %s / unbounded read | no bound, no filtering on length | full bytes allowed |
| read(fd,buf,n) with n controlled | n may exceed the buffer | length trick |
| fgets/readline | stops at newline | no \x0a in payload |
| memcpy/strcpy of counted length | bounded by a computed n | influence n |

## Falsifier

Falsifier — the read is bounded to less than the saved-state distance: no write reaches the return address; not this class.
