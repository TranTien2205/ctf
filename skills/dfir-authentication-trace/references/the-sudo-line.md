# sudo lines — escalation with target

`sudo: U : TTY=pts/1 ; PWD=/home/U ; USER=root ; COMMAND=...` —
the target account and full command in one line; `useradd` lines
carry the new uid/gid.

## Escalation

USER=target + COMMAND=full — one line.

## Full

USER + COMMAND in one line.
