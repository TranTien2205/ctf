# PSReadLine history — commands, no timestamps

`...\PSReadLine\<Host>_history.txt` — ConsoleHost vs
"Visual Studio Code Host" differ; grep the directory, not one name.
No timestamps; `SaveIncrementally` default = one $J DATA_EXTEND per
command. PSReadLine scrubs password/token/secret lines — absence
proves nothing.

## Ordered

No timestamps; secrets scrubbed by design.

## The scrub

Secret lines absent by design.
