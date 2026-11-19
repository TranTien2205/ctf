# The call-site args — what the redirect actually receives

A %n-to-GOT redirect lands on your target, but the CALL's arguments come
from the call site, not your fmtstr: puts(x) calls your target with x in
rdi. If x isn't a useful arg, the redirect is useless.

## The check

Before writing GOT[x], check what x is at the call: if puts is called
with a string you control, the redirect calls system(your_string). If
not, the redirect fires with the wrong arg.
