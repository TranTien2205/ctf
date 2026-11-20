# Stateful servers — the session matters

The service may remember answers across connections (cookie line,
token round-trip) — reconnecting can reset progress or resume it;
the banner on reconnect tells which.

## The session

The reconnect banner says resume vs restart.
