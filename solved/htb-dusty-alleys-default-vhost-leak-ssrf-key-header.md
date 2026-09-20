# Dusty Alleys — SOLVED (writeup-assisted)

- Platform: HackTheBox (web). Landing page titled "Underground Labyrinth".
- Date: 2026-09-19
- Target supplied: `http://154.57.164.82:30316` (black-box)
- Stack: nginx in front, Express behind (`X-Powered-By: Express`), `node-fetch/1.0`
- Flag: redacted; verified live in the `/guardian` SSRF response
- Assistance: writeup used after local evidence stopped producing hypotheses; recorded here.

## Chain

1. `GET /` is a **static file** (`Last-Modified`, `ETag`, `Accept-Ranges: bytes`, no
   `X-Powered-By`): a story page with a dead `<button>Interact with the Robot</button>`
   and no JavaScript at all. `robots.txt` 404s. Only `/` and `/evil-robot.jpg` exist.
   The image is clean (no trailing data past the JPEG EOI, no EXIF).
2. Directory enumeration is what opens the challenge. `common.txt` finds nothing;
   **`raft-medium-directories.txt` finds exactly one path: `/think`**, which nginx
   proxies to Express. It answers with the request headers as JSON:
   `{"host":...,"x-real-ip":...,"x-forwarded-for":...,"user-agent":...}`
3. Mapping that backend: only `/think` exists (nothing under `/think/`), GET/HEAD only,
   nginx preserves the path (`/think/flag` reaches the backend verbatim as
   `/think/flag`, per Express's `Cannot GET /think/flag`). nginx normalises `..`
   **before** location matching, so `/think/../x` falls back to the static root.
   Request smuggling is refused by nginx (CL+TE → 400, obfuscated TE → 501).
4. **The leak.** In HTTP/1.0 the `Host` header is optional, so a request without one
   is routed to nginx's `default_server` vhost — and `/think` echoes the Host that
   vhost supplies:
   ```
   curl -H "Host:" --http1.0 http://<target>/think
   → {"host":"alley.firstalleyontheleft.com", ...}
   ```
   That discloses the secret base domain `firstalleyontheleft.com`, which is what gates
   the rest of the application.
5. **The hidden vhost.** `Host: guardian.firstalleyontheleft.com` on the same port
   serves a different app entirely — "Dusty Alleys - The Game" — with
   `<form method="get"><input type="text" name="quote" placeholder="Enter the location of the key">`.
6. **SSRF with a credential attached.** `/guardian?quote=<url>` fetches the URL
   server-side with `node-fetch`, and attaches a `Key` header carrying the flag.
   Pointing it back at the header-mirror closes the loop:
   ```
   /guardian?quote=http://localhost:1337/think
   → {"key":"HTB{...}","user-agent":"node-fetch/1.0 (+https://github.com/bitinn/node-fetch)","host":"localhost:1337"}
   ```
   The internal port is **1337** — `127.0.0.1:1337` fails (the app resolves the vhost by
   name, and an IP literal produces `ERR_HTTP_INVALID_STATUS_CODE: Invalid status code: guardian`),
   and ports 3000 and 80 error. Only `localhost:1337` works.

## Reusable lessons

- **A header-mirror endpoint is not a curiosity, it is the exfiltration primitive.**
  Its value is that it prints whatever credential a *server-side* fetcher attaches.
  When an app has both an SSRF and an echo, aim the SSRF at the echo before anything else.
- **`--http1.0` with an empty `Host` is a one-line vhost-discovery probe.** HTTP/1.0
  makes `Host` optional, so nginx falls back to `default_server` and any endpoint that
  reflects the Host discloses the internal vhost name. Worth trying on every
  nginx-fronted target that reflects anything.
- **Wordlist size decided this challenge.** `common.txt` (4.7k) returned nothing and made
  the target look like a dead static page; `raft-medium-directories.txt` (~30k) found
  `/think` on the first pass. When a site looks empty but is clearly a challenge, the
  wordlist is the hypothesis being tested, not the target.
- The flavour text was the challenge name: "the air grows thick with **dust**" →
  *Dusty Alleys*. Distinctive story wording is a searchable identifier.
