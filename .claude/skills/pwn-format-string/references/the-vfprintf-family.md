# The vfprintf family — va_list forwarding


vfprintf/vprintf/vsnprintf take a va_list — a function that forwards its
variadic args to a v-printf call still exposes the format to your input.

| Call | Format position |
|---|---|
| vprintf(buf, args) | buf IS the format |
| vsnprintf(d,n,buf,args) | buf IS the format |
| a wrapper using va_list | forwards the args |

## Steps

1. The v-family takes format + va_list — your input as the format is
   still the bug.
2. A wrapper forwarding va_list exposes the format the same way.
3. Check whether your input reaches the format position through the
   va_list.

## Falsifier

The va_list carries a literal format and your input is an argument:
closed.
