# Bot triage — characterizing the delivery vehicle

The bot is the privileged viewer. Before crafting the payload,
characterize what the bot can reach, what session it holds, and how
it processes the page.

---

## 1. The bot surface — find the submission endpoint

```bash
# the endpoint that makes the bot visit a URL
grep -rnoE '(report|visit|admin-bot|preview|review|contact|check|submit|fetch-url|crawl)' \
  <src> --include='*.py' --include='*.js' --include='*.go' \
  --include='*.php' --include='*.rb' | head -30

# the browser library — what powers the bot
grep -rnoE 'puppeteer|playwright|selenium|chromedriver|headless|pyppeteer|splash|phantomjs|chrome|chromium|webkit' \
  <src> | head -20
```

## 2. The bot's launch context — the flags that matter

```bash
grep -rnoE 'args.*--|--disable|--no-sandbox|headless|userDataDir|incognito|SameSiteByDefault|disable-features|proxy|ignore-certificate' \
  <src> | head -20
```

The launch flags that change CSRF behavior:

| Flag | Effect |
|---|---|
| `--disable-features=SameSiteByDefaultCookies` | missing-SameSite = None — full CSRF surface |
| `--disable-features=BlockInsecurePrivateNetworkRequests` | PNA off — fetch to loopback works |
| `--disable-web-security` | CORS off — the page reads cross-origin (XSS-like) |
| `--no-sandbox` | the bot's browser is unsandboxed |
| `headless: 'new'` vs old | the chrome version → the SameSite default |
| `userDataDir` / a persistent profile | the cookie jar persists across visits |
| a fresh `incognito` per visit | the jar does NOT persist — no shared-jar |

## 3. The bot's credential — what session it holds

```text
- does the bot log in? → it holds a session cookie (SameSite applies)
- is the bot 'admin'? → its session is privileged
- does the bot just visit (no login)? → no cookie; the credential is
  its position (localhost) or a fixed context
- does the bot hold a flag in its context? → a cookie/localStorage/
  page-content the bot's browser carries
```

```bash
grep -rnoE 'login|setCookie|cookie|session|admin|flag|context\.|page\.goto|browser\.' <src> | head -40
```

## 4. The bot's network position — what it can reach

```text
the bot's browser resolves hosts from ITS context:
- 127.0.0.1 / localhost → the bot's own host — the TornadoService
  primitive
- a docker-compose service name (app:, web:, backend:) → the
  internal service — reachable to the bot, not you
- the challenge's own public URL → same as yours
- your external host → if the bot has internet egress
```

```bash
# the internal hostnames the bot resolves
grep -rnoE 'http://[a-z_-]+(:[0-9]+)?/|127\.0\.0\.1|localhost|0\.0\.0\.0|container|service|app:|web:|backend:|internal' \
  <src> --include='*.yml' --include='*.yaml' --include='*.conf' | head -30
```

## 5. The bot's visit lifecycle — what it does with the page

```text
- how long does it keep the page open? (a waitUntil / setTimeout /
  a fixed sleep) → the write must fire within that window
- does it scroll/click/interact? → a click-required CSRF needs the
  bot to click
- does it just load + close? → the write must fire on load — a
  synchronous form.submit() beats an async fetch
- does it run JS? → a bot that doesn't run JS needs a pure-HTML
  form + a click (rare — most run JS)
```

```bash
grep -rnoE 'waitUntil|setTimeout|sleep|waitFor|click|type|evaluate|goto|networkidle|domcontentloaded|load' <src> | head -20
```

## 6. The bot's request interception — what it blocks

```text
- does the bot intercept/block requests? (a page.setRequestInterception,
  a route.abort) → it may block your external beacons or non-target
  requests
- does it strip the URL? (a domain whitelist — only the challenge's
  own URLs allowed) → a data: URL or a hosted-on-target page
```

```bash
grep -rnoE 'setRequestInterception|route\.|abort|whitelist|allowlist|allowed|domain|startsWith|url.*match|blocked' <src> | head -20
```

## 7. The bot's output — does it return anything?

```text
- does the bot return a screenshot / page-content / the response?
  → you might READ the result directly (rare, but a read-oracle)
- does it just 200 'visited'? → fire-and-forget; the state-readback
  is the only oracle
- does it report an error? → a load-fail signal
```

## 8. The bot's visit count — the cycle budget

```text
- one visit per submission → each delivery attempt costs a cycle;
  batch your probes (multi-form chains, marker-per-attempt)
- a rate-limit on submissions → fewer cycles; be precise
- a queue → the visit is async; poll the oracle
```

## 9. The triage checklist

```text
□ what does the bot visit — a URL you supply?
□ what session does it hold — a cookie, a position, a fixed context?
□ does its jar persist across visits?
□ what hosts can it reach — loopback, internal names, your host?
□ does it run JS — how long does it keep the page?
□ does it block requests — a whitelist, a PNA rule?
□ does it return anything — a screenshot, a status?
□ how many visits per submission — the cycle budget?
```

## 10. The bot→payload mapping

| Bot trait | The payload shape |
|---|---|
| a session cookie + SameSite=missing | full form/fetch CSRF |
| a session cookie + Lax | GET-write top-nav only |
| localhost-position credential | a form POST to 127.0.0.1 (not fetch — PNA) |
| a persistent shared jar | login-CSRF cookie-swap (SSOS) |
| a fresh jar per visit | single-cycle — no cross-cycle state |
| a domain whitelist | a data: URL or a hosted-on-target page |
| a short visit window | a synchronous form.submit(), not fetch |
| no JS execution | a pure-HTML form + a click (rare) |
| blocks external requests | an internal target or a data: page |
