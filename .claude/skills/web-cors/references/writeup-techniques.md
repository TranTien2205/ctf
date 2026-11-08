# web-cors — techniques reported in public CTF writeups

**This is published knowledge, not local experience.** Nothing here was solved
in this repository. `evidence_level` for this class stays `catalogue` and
this class's field notes stay a template stub on purpose: that stub is the
honest backlog of classes nothing here has solved.
Every claim below carries the writeup URL it came from and a verbatim span
from the fetched page. A writeup's own claim is not verification.

Source: 18,493-URL public writeup catalog, fetched and distilled
2026-09-26; each card was checked by a second pass that rejected 48 of 150.


## 1. Treat a server-side Origin allowlist as an authorization check rather than a browser hint: read the allowed value out of the response's Access-Control-Allow-Origin header (or the front-end bundle) and replay the request from curl/Burp — or a raw WebSocket handshake — with that exact Origin header set.

- **status**: `writeup-claimed` — no target was probed for this here
- **why it works**: Only a browser is bound by the same-origin policy; the Origin request header is fully attacker-controlled from any other client. When the server branches on Origin to decide what body to return, instead of merely deciding which ACAO value to echo, nothing enforces the check, and the server itself discloses the value it wants in ACAO or in the WebSocket handshake error.
- **first probe**: curl -is http://TARGET/ | grep -i '^access-control' to learn the expected origin, then replay the identical request with -H 'Origin: <that value>' and diff the two bodies.
- **expected signal**: The second response body differs from the first: the secret data or the flag appears where the header-less request returned an error, an empty page, or a 'bad origin' rejection naming the expected host.
- **falsifier**: The two bodies are byte-identical, or ACAO merely mirrors whatever Origin you send while the body never changes — then the origin check is advisory and the data is gated by something else (session cookie, path, auth header).
- **sources** (4):
  - Texas Security Awareness Week 2024 — https://nightxade.github.io/ctf-writeups/writeups/2024/Texsaw-CTF-2024/web/extreme-security.html
    > Access-Control-Allow-Origin: https://texsaw2024.com So that’s what our origin needs to be.
  - Texas Security Awareness Week 2024 — https://nightxade.github.io/ctf-writeups/writeups/2024/Texsaw-CTF-2024/web/extreme-security.html
    > Connection: close Origin: https://texsaw2024.com And we get the flag!
  - AppSec-IL 2020 CTF — https://ctftime.org/writeup/24418
    > Upgrade: websocket Origin: https://securityocean.corp.local Sec-WebSocket-Version: 13
  - AppSec-IL 2020 CTF — https://ctftime.org/writeup/24418
    > By spoofing the origin header to bypass CORS restrictions, valid WebSocket requests can be made to extract sensitive information.

## 2. When the API answers Access-Control-Allow-Credentials: true alongside a single pinned Access-Control-Allow-Origin, stop attacking the API cross-origin and instead obtain script execution on the one origin named in that header; from there an XHR with withCredentials reads the authenticated response.

- **status**: `writeup-claimed` — no target was probed for this here
- **why it works**: The credentialed CORS mode forbids a wildcard, so the browser hands the response only to that exact origin — which makes the allowlist a map naming the single origin worth owning. Any XSS, JSONP or script-injection foothold on that origin is therefore upgraded into an authenticated read of the API, even when the foothold sits on a sibling subdomain that the API refuses directly.
- **first probe**: curl -is https://API/<authenticated endpoint> -H 'Origin: https://evil.example' | grep -i '^access-control' and compare against the same request with no Origin header.
- **expected signal**: Access-Control-Allow-Credentials: true together with an Access-Control-Allow-Origin that is a fixed app origin — neither reflected back from your Origin nor '*'. That fixed origin is the pivot target.
- **falsifier**: ACAO is absent, or it is '*' with no ACAC: true, or it does not reflect your evil origin and no credentialed mode exists — then no cross-origin read of authenticated data is available and CORS is not the way in.
- **sources** (3):
  - VolgaCTF 2020 Qualifier — https://spotless.tech/volgactf-2020-qualifier-user-center.html
    > curl -is https://api.volgactf-task.ru/user | grep Access Access-Control-Allow-Credentials: true Access-Control-Allow-Origin: https://volgactf-task.ru
  - VolgaCTF 2020 Qualifier — https://spotless.tech/volgactf-2020-qualifier-user-center.html
    > By exploiting CORS and the api_server cookie in combination with JSONP requests, it is possible to execute arbitrary scripts on the main domain.
  - Facebook CTF 2019 — https://s1r1uss.blogspot.com/2019/06/facebook-ctf-2019-writeup_2.html#product
    > And expecting Allow-Contol-Allow-Origin: * and Access-Control-Allow-Credentials: true. :) But it is protected from CORS.
