# The redirect effect — what the write actually triggers


The %n write alone does nothing — it changes a pointer that a later call
reads. The redirect's effect IS the exploit:

- GOT[x] written → the next call to x goes to your target.
- ret-addr written → the function's return goes to your target.
- __free_hook written → the next free calls your target.
- A vtable/handler written → the next indirect call redirects.

The write plants; the redirect fires.
