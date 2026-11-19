# The print-object op — blessed leaks


If the service has a "print details" op that shows an object's fields,
the fields may include pointers — a sanctioned leak.

## Check

- Does show() print any pointer-valued field? That's a free heap leak.
- Does it print raw memory or only safe fields?

## Falsifier

No pointer field is printed: the channel is data-only.
