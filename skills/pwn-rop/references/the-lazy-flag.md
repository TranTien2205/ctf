# RTLD_LAZY — the deferred resolve


Lazy binding: the first call resolves the symbol — the GOT holds the
resolver stub until then; the leak must read a called function's
slot.
