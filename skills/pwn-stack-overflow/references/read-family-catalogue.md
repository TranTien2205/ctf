# The read-family matrix — which input function and what it allows — case catalogue

Different input functions allow different byte filters and bounds — the read function decides which shellcode/chain bytes survive.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | gets()/scanf %s / unbounded read | no bound, no filtering on length | full bytes allowed |
| 2 | read(fd,buf,n) with n controlled | n may exceed the buffer | length trick |
| 3 | fgets/readline | stops at newline | no \x0a in payload |
| 4 | memcpy/strcpy of counted length | bounded by a computed n | influence n |

## Falsifier

Falsifier — the read is bounded to less than the saved-state distance: no write reaches the return address; not this class.
