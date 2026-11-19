# RPATH/RUNPATH — the library search path


The binary's library search path decides which libc loads — a writable
or hijackable path loads YOUR libc — an LD_PRELOAD-class trick when
the path is writable.
