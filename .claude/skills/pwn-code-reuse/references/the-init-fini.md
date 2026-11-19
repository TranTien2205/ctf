# .init/.fini — the startup-ending arrays


.init_array/.fini_array hold function pointers run at startup/exit —
a write there redirects program setup/teardown to your function.

## The use

On partial RELRO, .fini_array is writable — an exit-time redirect
target.
