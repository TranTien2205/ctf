# Signals — SIGINT/SIGTERM mid-run

A Ctrl-C mid-round should still flush the round log — install a
handler or use unbuffered log writes; the log is the debugging
asset, losing it loses the run's evidence.
