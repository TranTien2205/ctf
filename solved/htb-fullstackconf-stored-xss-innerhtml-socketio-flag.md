# xss ("Full Stack Conf") — SOLVED (self-solved)

- Platform: HackTheBox (web). Page meta author: makelarisjr, makelaris.
- Date: 2026-09-18
- Target supplied: `http://154.57.164.82:32040` (black-box)
- Stack: `Server: Werkzeug/1.0.1 Python/3.8.6`, Flask + Flask-SocketIO
- Flag: redacted; verified live in a socket.io frame pushed by the server
- Cost: 5 probes in `web-xss`, ~20 minutes. Budget was not exhausted.

## Chain

1. `GET /` → 200, `<title>xss</title>`. The page states the objective in plain
   text: *"Stay up-to-date on Full Stack Conf or pop an alert() to get the flag"*.
2. The inline script gives the only two pieces of surface:
   - `fetch('/api/register', {method:'POST', body: JSON.stringify({email: ...})})`
   - a socket.io client, commented `// not part of the challenge`, that listens
     for a `flag` event and `alert()`s `data.flag`.
   The comment is misleading: that socket is the **only** channel the flag is
   ever delivered on. It is not part of the bug, but it is all of the exfil.
3. Route enumeration: only `/` and `/api/register` exist. `/admin`, `/emails`,
   `/list`, `/panel`, `/dashboard`, `/bot` and `/api/emails` all return Werkzeug's
   404, and `GET /api/register` returns `405` with `Allow: OPTIONS, POST`.
   The page that renders the email is not reachable by the player.
4. The submitted email is **never reflected to the submitter**: `GET /` is
   byte-identical (5728 bytes) before and after registering a marker, and seven
   query-parameter names produce no reflection either. So the sink is only
   observable through its side effect on the bot.
5. The transport is socket.io v2 (`EIO=3`), `"upgrades":[]` — polling only, and
   the server **holds each poll open until it has something to send**. That is
   what makes the channel a usable oracle: an empty long-poll is a real negative,
   not a transport failure.
6. Holding one long-poll open and posting `<img src=x onerror=alert(1)>` as the
   email returns, within about thirty seconds:
   `54:42["flag",{"flag":"HTB{...}"}]`

## Which payload actually fires

Tested individually, one payload per socket, 100-second window each:

| payload | result |
|---|---|
| `<img src=x onerror=alert(1)>` | **FIRED** |
| `"><img src=x onerror=alert(1)>` | **FIRED** |
| `<script>alert(1)</script>` | no flag event (one trial) |

A `<script>` element that does not run while an `onerror` handler does is the
signature of **insertion through `innerHTML`**: HTML parsed that way inserts the
script node but never executes it, whereas the image's error handler fires
normally. The leading `">` is unnecessary — it is inserted as text, which is
consistent with an element body rather than an attribute.

The `<script>` negative rests on a single trial and is recorded as such, not as
an established fact. See the anomaly below for why one trial is not enough here.

## Anomaly worth recording

The very first attempt posted `"><img src=x onerror=alert(1)>` while polling for
90 seconds and saw **no packet at all**. A later, deliberately identical test of
the same payload fired within ~30 seconds. The difference is not explained by
anything observed, so the first result is logged as `inconclusive` rather than
as a negative. Practical consequence: on a bot-driven challenge, **one silent
run is not evidence that a payload fails.** Re-run before discarding a payload.

## Reusable lessons

- **Read the comment that says it is not part of the challenge.** It named the
  event and the delivery channel; without it there is no way to observe success.
- **Establish the oracle before the payload.** Forty seconds of watching raw
  frames proved the server holds polls open until an event exists. Without that,
  every empty response is ambiguous and every negative is worthless.
- **Batch payloads across contexts, then bisect.** Ten payloads on one open
  socket found a hit quickly; three single-payload runs then identified exactly
  which one worked. Batching first and bisecting after is much cheaper than one
  payload per socket from the start, and it stays inside the probe budget.
- **`<script>` failing while `onerror` succeeds is diagnostic, not noise** — it
  identifies `innerHTML` insertion without ever seeing the vulnerable page.
