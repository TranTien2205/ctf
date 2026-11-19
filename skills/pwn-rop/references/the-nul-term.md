# The NUL terminator — the string's end


C strings end at 0x00 — a planted "/bin/sh" needs the trailing zero;
an off-by-one miss gives system "/bin/sh<garbage>".
