# Edge catalogue 2 — the rarer states, indexed

## The bot with a custom UA or headers

Some bots set a specific `User-Agent` or custom headers — the
reproduction must match them, and a payload that reads the UA may
need to distinguish the bot from a real user. Reproduce via
`--user-agent` or `set_user_agent`; read `navigator.userAgent` to
confirm what the payload sees.

## The bot behind a proxy

A bot whose traffic routes through a proxy (`--proxy-server`) changes
the network path — your exfil may route through a proxy the bot
trusts, or your tunnel may be unreachable through it. Reproduce the
proxy flag; test the channel through the same path.

## The bot with an extension

A bot that loads a browser extension (`goog:chromeOptions.extensions`)
changes the page's environment — the extension may inject content
scripts, block requests, or expose a surface. Reproduce it only if the
bot's spec names it.

## The bot running non-headless

A bot that runs headed (a visible window, `xvfb`) renders identically
but behaves differently on some timing/focus edges — the reproduction
still uses headless for the debug loop; the difference rarely matters
unless the payload depends on focus/visibility events.

## The session that outlives the command

A session idle between commands lives until `DELETE` — a long
multi-step read (a directory walk via `file://`) can hold a session
for minutes. Keep the walks targeted — a specific path, not a crawl —
and delete on completion.

## The endpoint that serialises one browser

A single-browser driver that only allows one session at a time — a
second `POST /session` queues or takes the browser over. On a shared
instance, your session may collide with the challenge's own bot or
another team's — keep sessions short and clean.

## The `data:`/`about:`/`javascript:` navigation

`file://` is the usual read scheme, but `data:text/html,<script>`,
`about:blank`, and (in older drivers) `javascript:` URLs can also be
navigated — a `data:` URL loads attacker-controlled HTML in the
browser, a separate primitive from `file://` for when file access is
blocked but navigation is not.

## The read that returns a download

A `file://` nav to a binary or a MIME-typed file may trigger a
download instead of a render — `source` returns nothing useful. The
read path: `execute` `fetch` the file + base64, or a `data:`-wrapped
read.

## The Grid node's different filesystem

A Grid node's `file://` is the *node's* filesystem — the flag may be
on the app's container, not the node's. The node is a different host;
the read primitive is the same but the filesystem differs.

## The cookie that needs a path/domain

An `add_cookie` with the wrong `domain`/`path` does not reach your
page — the cookie sits in the jar but is not sent to your URL. Match
the bot's exact `domain` and `path`; verify with `GET /cookies`
filtered to the page's origin.

## The flag rendered in an iframe's source

A flag rendered in a cross-origin iframe is in the frame's `source`,
not the top's — `switch_to.frame` into it before `GET /source` or
`execute`.

## The wait that is an event, not a timer

A bot that waits on `networkidle`, a `wait_for_selector`, or a promise
— the payload must trigger the condition, not just outlast a timer.
A `networkidle` wait extends for every request your payload makes.
