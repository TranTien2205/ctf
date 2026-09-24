# noted (picoCTF 2022) — web

Flag read from a live response. Value not recorded here.

## Shape
Fastify + EJS. Note title and content are rendered unescaped (`<%-`), but notes are
per-user, so it is self-XSS. The report bot registers its OWN account, stores the flag
in its own note, then visits the reported URL. No CSP, cookie not HttpOnly.
`/new` is CSRF-protected; **`/login` is not**.

## Chain
1. Report a `data:text/html,...` URL — it executes under the bot's `page.goto`.
2. **Every URL inside the payload must be the app's internal address
   `http://0.0.0.0:8080`** — the bot has no internet and cannot resolve the public host.
3. `window.open(I+"/notes","flag")` renders the bot's flag note into a NAMED window
   (top-level navigation, so the SameSite=Lax cookie is sent).
4. A form POST to `/login` with our credentials swaps the session and lands on
   `/notes`, firing our stored self-XSS.
5. That XSS is now same-origin with the flag window: read it and re-post the flag as a
   note in our own account.

## Traps
- `target="_blank"` carries implicit `noopener`, putting the XSS window in a SEPARATE
  browsing-context group, so `window.open("","flag")` cannot resolve the name and
  silently returns a fresh blank window. Symptom is `win=y` with `href=about:blank`,
  which looks exactly like popup blocking. Use a NAMED target.
- A top-level `data:` URL does NOT execute when Chrome is given it as a CLI argument,
  but DOES under the bot's CDP-driven navigation. Test the right path or you will
  discard a working technique.
- With no egress, have the payload post its own diagnostics back as notes. That is what
  turned this from guesswork into three targeted fixes.
