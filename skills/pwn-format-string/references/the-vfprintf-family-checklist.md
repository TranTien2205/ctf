# The vfprintf family — va_list forwarding — checklist

Companion to `the-vfprintf-family.md`.

## Checklist

- [ ] Call | Format position
- [ ] vprintf(buf, args) | buf IS the format
- [ ] vsnprintf(d,n,buf,args) | buf IS the format
- [ ] a wrapper using va_list | forwards the args
- [ ] 1. The v-family takes format + va_list — your input as the format is
- [ ] 2. A wrapper forwarding va_list exposes the format the same way.
- [ ] 3. Check whether your input reaches the format position through the
