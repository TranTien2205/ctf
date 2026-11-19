# The complete printf family — every call that takes a format — checklist

Companion to `the-printf-family-complete.md`.

## Checklist

- [ ] Function | Format arg | Output
- [ ] printf | arg 1 | stdout
- [ ] fprintf | arg 2 | a FILE stream
- [ ] sprintf | arg 2 | a buffer (overflow-able)
- [ ] snprintf | arg 3 | a bounded buffer
- [ ] vprintf/vfprintf/vsprintf/vsnprintf | format + va_list | varies
- [ ] dprintf | arg 2 | an fd
- [ ] asprintf | arg 2 | allocates a string
- [ ] syslog | arg 2 | the syslog
