# TLS — the thread-local structures


Thread-local storage and the DTV — the thread-pointer structures;
the canary itself lives in the TLS on x64 (fs:0x28).

## The canary's home

fs:0x28 — the TLS slot the epilogue checks; a direct write to it
(rare) or a leak of it bypasses the check.
