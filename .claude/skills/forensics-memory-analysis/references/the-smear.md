# Memory smear — the caveat

A live-captured image has inconsistent structures (the machine kept
running during capture) — a torn pslist or half-updated list. Note
it; re-derive rather than trust a single walk. Crashdumps are
consistent (frozen at the bugcheck).
