# Reconnect + resume

A dropped socket mid-run: know whether the server keeps state (same
round back?) or resets — re-capture the banner on reconnect; the
round counter may restart.

## The banner

Reconnect re-reads the banner — resume vs restart.
