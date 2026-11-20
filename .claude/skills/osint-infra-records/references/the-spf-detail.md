# SPF — the mail policy + a planted token

`v=spf1 ...` authorizes senders — and a challenge can plant a flag
inside an include or a custom mechanism. Read the whole record.

## The shape

`v=spf1 mx include:_spf.other.com ~all` — the include and the
mechanisms can hide a planted domain; read the full string, not
just the `v=`.

## The mechanisms

v=spf1 + mechanisms (mx, a, include, ip4, ptr, all) — an include can name a sibling domain whose own records are next.
