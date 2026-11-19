# Timeouts — the response's clock


Every recv needs a timeout — a hang isn't a result; the timeout's
length matches the target's latency (a remote service needs seconds,
not milliseconds).
