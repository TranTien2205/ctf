# The vfprintf family — va_list forwarding — map

Companion to `the-vfprintf-family.md`.

| Call | Format position |
|---|---|
| vprintf(buf, args) | buf IS the format |
| vsnprintf(d,n,buf,args) | buf IS the format |
| a wrapper using va_list | forwards the args |
## Steps
## Falsifier
