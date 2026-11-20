# CRLF vs LF — the wire ending

A transcript captured interactively hides `\r\n` — log raw bytes;
if the terminator is `\r\n`, matching `\n` still works but echo
parsing must strip `\r`.

## The ending

Log raw bytes; strip \r on echo lines.
