# TornadoService — SOLVED (assisted: writeup)

- Platform: HackTheBox (web)
- Date: 2026-09-06
- Flag: `HTB{REDACTED}` (200 from /stats with forged cookie)
- Artifacts: `~/ctf/challenges/tornadoservice/serve.py` (exploit page + localhost.run tunnel)
- Writeup used: ctfbase writeup + Qtlas README (found via websearch after manual recon)

## Chain

1. Fingerprint: Tornado 6.4.1 dashboard; endpoints `/get_tornados`,
   `/update_tornado` (403 "Only localhost"), `/report_tornado?ip=`
   (headless-Chrome bot visits `http://{ip}/agent_details`), `/login`, `/stats`.
2. Header IP-spoofing (XFF/X-Real-IP/Forwarded/Host) does NOT pass the localhost
   check — `remote_ip` is the socket peer.
3. Chain: bot (localhost browser) -> our tunnel page -> CSRF form
   (`enctype=text/plain`) POST to `http://127.0.0.1:1337/update_tornado` with
   Python class-pollution JSON:
   `{"machine_id":"<real id>","__class__":{"__init__":{"__globals__":{"APP":{"settings":{"cookie_secret":"NEWSECRET123"}}}}}}`
   (+ fallback iframe `postMessage` -> `innerHTML` XSS -> same-origin fetch).
4. Class pollution overwrites `APP.settings.cookie_secret`.
5. Forge Tornado v2 signed cookie
   (`create_signed_value(SECRET, "user", "lean@tornado-service.htb")`),
   `GET /stats` -> flag.

## Reusable lessons

- **Hosting for bot challenges**: ngrok free inserts a browser interstitial that
  headless bots cannot pass; `localhost.run` SSH reverse tunnel has no interstitial.
  Fingerprint interstitial BEFORE burning bot triggers (curl with browser UA).
- **text/plain CSRF -> JSON**: body = `name` + `=` + `value` + `\r\n`; put the `=`
  inside a string key and close the JSON in `value` (no encoding applied).
- **Python class pollution**: recursive `setattr` merge + module-level object
  reachable via `__class__.__init__.__globals__` (same family as nginxatsu merge bug).
- Two payloads fired simultaneously (form + iframe-XSS) — success could not be
  attributed to one route; for clean attribution fire one, wait, then the other.
- Both solves required a valid `machine_id`/existing object fetched from a public
  read endpoint first — enumerate public reads before attacking the write path.

---

## Re-solved 2026-09-20 — self-solved, and the route question is now settled

Second instance (`154.57.164.82:30292`, "Tornado Dashboard v2.7.7"). Same image:
`ffuf` over `raft-medium-words` returned exactly `login` and `stats`, which matches
`make_app()` handler-for-handler, and the flag is unchanged.

No writeup this time. The chain card's `first_confirming_probe` ran first and held
(`/get_tornados` gives a live `machine_id`; direct `POST /update_tornado` answers
403 "Only localhost can update tornado status.").

### What this run added

**1. Header spoofing is dead, measured not assumed.** Seven headers — `X-Forwarded-For`,
`X-Real-IP`, `Forwarded`, `X-Originating-IP`, `X-Client-IP`, `True-Client-IP`,
`Host: localhost` — all still returned the 403. `is_request_from_localhost()` reads
`handler.request.remote_ip` and the server runs without `xheaders`, so the value is the
socket peer. The bot relay is mandatory, not merely convenient.

**2. The two payload routes were finally separated — and only one works.**
The first solve fired the `text/plain` form and an iframe/`postMessage` XSS at the same
time and could not attribute the success. This time each route was tested alone against
a **local replica built from this same source** and driven by a real headless Chrome:

| Route | Chrome 152 (replica, private -> loopback) | Chrome 127 (real bot, public -> loopback over http) |
|---|---|---|
| `fetch` GET `/get_tornados` (simple, no preflight) | **works**, readable via `ACAO: *` | **blocked** — `TypeError: Failed to fetch` |
| `fetch` POST `Content-Type: application/json` | **blocked** — `TypeError: Failed to fetch` | **blocked** |
| `<form enctype="text/plain">` navigation | **works** | **works** |

The blocker is **Private Network Access**. A preflighted subresource request to a
loopback address is refused, and from an *insecure* public origin even the simple GET is
refused, because PNA requires a secure context for private-network requests. A **form
navigation is not a subresource**, so PNA never applies to it. That is why the form is
the only route that survives, on both Chrome versions.

Practical consequence: the bot cannot be used to discover the internal port when the
exploit page is plain `http://` on a public host. Fire the form blind at a port list
instead — `1337, 80, 8000, 8080, 5000, 3000, 1338, 8888` — and take the `machine_id`
from the public `/get_tornados`, which lists the very same objects.

**3. Attribution was proved, not inferred.** The form body carries a dummy key whose
only purpose is to absorb the `=` that `enctype=text/plain` inserts:

```
{"machine_id":"host-1051","ignore":"=","__class__":{"__init__":{"__globals__":{"APP":{"settings":{"cookie_secret":"..."}}}}}}
```

After the bot ran, `/get_tornados` showed
`{"machine_id": "host-1051", ..., "ignore": "="}` — exactly one object, carrying a marker
that only the `text/plain` encoding can produce. `setattr` on `TornadoObject` makes the
dummy key visible through `vars()`, so it doubles as a free success oracle: no need to
guess whether the pollution landed.

### Reusable lessons (new)

- **Rehearse a bot chain against a local replica before spending a trigger.** The source
  was on disk, so the whole chain — pollution, `create_signed_value` forgery, `/stats` —
  was proved offline first. Every real bot trigger then had a known-good payload behind it.
- **Private Network Access, not CORS, is what kills browser-relayed SSRF into loopback.**
  `Access-Control-Allow-Origin: *` is a red herring here: the app permits the read, the
  *browser* refuses to send it. Reach for a navigation (form, top-level, iframe) rather
  than `fetch` whenever the victim address is loopback or RFC1918.
- **Give the payload a harmless marker field.** In a `setattr` merge the extra key shows up
  in the public read endpoint, turning a blind cross-origin write into a verifiable one.
