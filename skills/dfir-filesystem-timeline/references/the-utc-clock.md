# Fix the clock — everything is UTC

FILETIME in `$I`, `$J`, LNK and DestList is UTC; a question quoting
local time quotes what Explorer rendered. `mactime -y` emits UTC
ISO — `-z`/`-m` do not work with `-y`; `istat` prints host-local.
