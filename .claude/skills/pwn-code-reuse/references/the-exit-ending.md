# The exit ending — a clean finish


exit(code) ends the process cleanly — the preferred last entry when
the flag already printed and a crash would be noise.

## The chain

    ... [exit@plt or the exit gadget] [code if needed]
