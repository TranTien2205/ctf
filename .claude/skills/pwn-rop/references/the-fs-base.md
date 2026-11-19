# fs base — the thread pointer


fs points at the TLS/TCD — the canary, the stack guard, the locale —
a leak of the fs base or the canary's slot is the canary-bypass input.
