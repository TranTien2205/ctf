# SameSite and cookie — the cookie's reach per channel

Each SameSite mode, what it allows, and the channel that works.

---

## 1. SameSite=Lax — the default gate

```text
a Lax cookie — a cross-site fetch doesn't carry it; a TOP-LEVEL
NAVIGATION does. the bot's cross-site fetch to your page is non-
credentialed; a same-site navigation (a meta-refresh issued BY THE
TARGET) carries it.
```

## 2. SameSite=Strict — the stricter gate

```text
a Strict cookie — even a top-level navigation doesn't carry it on
a first-party-only case — the strictest gate. a sealed shape's
same-site design still works — the bot's request to the target
itself is same-site.
```

## 3. SameSite=None + Secure — the credentialed read

```text
a None+Secure cookie — a cross-site fetch carries it — a
credentialed cross-site read — the classic shape's whole channel
carries the cookie.
```

## 4. The meta-refresh — a same-site navigation bypass

```text
a meta-refresh issued BY THE TARGET is a same-site navigation —
it carries the Lax cookie a cross-site fetch wouldn't. the sealed
shape's whole design avoids the cross-site cookie question — the
bot's request to the target itself is same-site.
```

## 5. The same-origin stored page — the Lax cookie rides

```text
a stored page on the target's origin — the bot's navigation to it
is same-site — the Lax cookie rides — a same-origin CSS/JS channel
carries the cookie.
```

## 6. The per-channel cookie-reach

```text
a cross-site fetch to YOUR page     — a Lax/Strict cookie doesn't ride
a same-site navigation (meta-refresh)— a Lax cookie rides
a same-origin stored page           — a Lax cookie rides
a sealed-shape server-state channel — no cookie question — the read is
                                       a server-state read, not a cookie-carry
a SameSite=None + Secure             — a cross-site fetch carries it
```

## 7. The SameSite-check — which mode the cookie uses

```bash
# the cookie's SameSite attribute
curl -sI "$BASE/" | grep -i 'set-cookie'
#   SameSite=Lax|Strict|None — the mode
```

## 8. The partition — the :visited and cache's per-site limit

```text
a partitioned :visited and cache (per top-frame site) — a link to a
URL the victim visited on ANOTHER site doesn't style visited; a
resource cached on site A isn't shared with site B — the history/
cache oracles are same-site or a rendering-side-channel only.
```

## 9. The SameSite-and-sealed-shape relationship — the design

```text
the sealed shape's whole design avoids the cross-site cookie
question — the bot's request to the target itself is same-site —
the Lax cookie rides. the classic shape's cross-site fetch hits the
gate — a SameSite=None cookie or a same-site navigation is needed.
```

## 10. The cookie-context — whose session the leak reads

```text
the leak reads under the BOT's session — a flag cookie, an admin
context, or a plain visitor. a plain-visitor bot reads a plain
session — the flag isn't in it — verify the bot's cookie.
```
