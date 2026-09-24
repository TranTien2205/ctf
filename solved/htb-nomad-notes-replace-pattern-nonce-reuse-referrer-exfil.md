# Nomad Notes (Carta) — SOLVED (self-solved)

- Platform: HackTheBox. Target: `154.57.164.82:32634`. Source supplied.
- Stack: Express 5 + puppeteer bot, no datastore of any kind.
- CSP: `default-src 'none'; connect-src 'self'; script-src 'nonce-<random>'; style-src 'self';
  img-src 'self'; frame-src 'none'; object-src 'none'; base-uri 'none'; form-action 'self';
  frame-ancestors 'none'; require-trusted-types-for 'script';`
- Flag: only ever exists inside the URL the bot is sent to. Value not committed.

## The two bugs

1. **The template engine replaces with `String.replace(str, value)`.** That makes the `$`
   replacement patterns live: `` $` `` expands to the text *before* the match, `$'` to the
   text after. The loop walks the data object in key order and `nonce` comes first, so by the
   time the user-controlled field is substituted, the real CSP nonce is already sitting in the
   prefix of that same line. A payload of `` $` `` therefore copies the live nonce into the
   output and lands attacker JS **inside the legitimately-nonced script element** — the
   `escape()` on the value never mattered, because no markup was needed.
2. **`/destinations` reflects its `name` parameter unescaped** (every other view escapes),
   and the privileged branch of `/report` puts the flag into exactly that page's URL.

## Chain

1. `POST /report` with `path=postcard?secret=<payload>` → non-privileged branch → the bot
   visits our crafted postcard.
2. The `` $` `` payload executes with a valid nonce and issues a **same-origin `fetch`** to
   `/report` carrying the `x-carta-auth-key` header. A custom header is the whole point: a form
   or plain CSRF cannot set one, so script execution inside the bot is mandatory.
3. The server now sees loopback + matching `Origin` + the header → privileged branch → it sends
   the bot to `/destinations?name=<our header>&flag=<FLAG>`.
4. Our header value is reflected raw into that page. It opens with `</title>` to escape the
   title element and plants `<meta name="referrer" content="unsafe-url">` plus a meta refresh.
5. The bot navigates out and the **Referer carries the full URL, flag included**.

## Constraints that shaped the payload

`escape()` removes `< > & " '`, so stage 1 can use no quotes and no arrow functions (`=>`
contains `>`). Backticks, `function(){}`, `atob()` and `+` are the entire toolkit; the stage-2
markup travels base64-encoded inside `atob()`.

## What cost time, and the lesson in each

- **ngrok's free interstitial keys on User-Agent.** Every request from a headless-Chrome bot —
  navigation, `<script src>`, image — is answered by ngrok's edge and never reaches the agent.
  A plain `curl` smoke test passes and gives false confidence. I burned several probes reading
  "no callback" as "exploit failed" when the exploit was partly working. **Verify an exfil
  listener with a browser User-Agent before trusting any negative result.**
- **Referrer policy.** An A/B test proved the point: without the meta the Referer was just
  `http://localhost:3000/` (default `strict-origin-when-cross-origin` drops path and query);
  with `unsafe-url` the full URL and flag came through.
- **Express 5 leaves `req.body` undefined when no body parser matched.** The stage-1 `fetch`
  sent no `Content-Type`, so destructuring `req.body` threw and `/report` answered 500 — the
  chain died silently. Making the XSS report `r.status` back to the listener found it in one
  shot. **When a blind chain stalls, spend a probe making the payload narrate itself.**
- Trusted Types matters for the *alternative* exfil: `script.src = <string>` is a
  `TrustedScriptURL` sink and throws under `require-trusted-types-for 'script'`. Navigation is
  not a TT sink, which is why the meta-refresh route is the robust one.

## Reusable lessons

- A template engine built on `.replace()` with untrusted data is a content-reuse primitive.
  Check the substitution ORDER: anything already substituted becomes reachable via `` $` ``/`$'`.
  Here that meant a nonce leak into an executable context.
- A nonce-based CSP is only as strong as the surrounding template: reusing an existing nonced
  script beats trying to forge a nonce.
- Strict CSP does not restrict navigation. When `connect-src`/`img-src` are `'self'`, the URL of
  the victim page plus `referrer: unsafe-url` is still a clean exfil channel.
- A gate that requires a custom request header is a deliberate "you must have XSS, not CSRF"
  marker; read it as a hint about the intended chain.
