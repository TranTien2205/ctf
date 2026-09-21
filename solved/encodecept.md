# EncoDecept — SOLVED

- HTB University CTF 2024, web, category "medium" (hardest web of the event).
- Target: Rails "Contract Frontend" behind an nginx caching proxy, with a Django API on an internal port.
- Flag read from a live response: `HTB{REDACTED}` (written into the Rails web root by the Marshal RCE, then fetched over HTTP).
- Assistance: writeup-assisted. The system identified the class and cache deception independently; the charset XSS technique and the Ruby 3.4 Marshal gadget were taken from public writeups after local evidence was exhausted.

## Stack

- nginx caching reverse proxy, extension-based cache (`\.(css|js|html|json|ico|...)$`), cache key `$uri$is_args$args`, `X-Cache-Status` header.
- Rails 7.2 frontend, `active_record_store` sessions, development mode (detailed error pages).
- Django REST API on `127.0.0.1:8080` reached only through the Rails app.
- `remove_charset_middleware` strips `; charset=...` from every response.
- Roles: `guest`, `contract_manager`, `administrator`.
- A report bot logs in as `contract_manager` and visits an attacker-supplied URL.

## Chain

1. Register/login a guest account.
2. Markdown bio on `/settings` is rendered by Redcarpet with `filter_html`. It is not directly XSS, but the response has no charset, so the browser sniffs the encoding.
3. Submit a bio that uses the JIS X 0208 1978 escape (`\x1b$@` ... `\x1b(B`) to break out of the `<img alt="...">` attribute and inject `onerror=...`:
   `![\x1b$@](x.png) \x1b(B ![b](onerror=eval(atob('<js>'))//)`
4. Web cache deception: request the authenticated `/settings.html?cb=N` so nginx caches the rendered page (with our XSS bio) under a static-looking URL.
5. Report `http://127.0.0.1:1337/settings.html?cb=N`. The bot renders the cached page and the XSS runs in the `contract_manager` session. `.ico` did not render (Chrome treated it as an image); `.html` did.
6. The XSS brute-forces the admin password through the ORM filter oracle:
   `GET /contracts/manage?owner__password__startswith=<prefix>&owner__username=admin`
   and counts whether the page still says "No contracts found".
7. Exfiltrate without an external listener: the XSS PATCHes the bot's own bio with the recovered password and navigates to `/settings.html?leak=1`, which nginx caches; the operator reads it anonymously.
8. Log in as admin. Create a contract template whose `data` form field overrides the controller's `Marshal.dump(params[:content])` because the controller does
   `{ data: serialized_content, user_id: ... }.merge(params.to_unsafe_h)`.
9. Viewing the template runs `Marshal.load(@template['data'])`. A Ruby 3.4 universal `Gem::RequestSet::Lockfile` gadget runs a shell command through the `zip` binary. First the detection gadget populates the git cache, then the RCE gadget runs:
   `-TmTT="$(cp /flag.txt /frontend/public/f.html)"any.zip`
10. Fetch `/f.html` and read the flag from the live response.

## Reusable

- An nginx cache keyed on the URI plus a Rails format extension (the `.` delimiter) gives web cache deception against authenticated pages.
- A response with no charset plus a Markdown renderer that emits attributes is an encoding-differential XSS primitive (JIS X 0208 1978 in Chrome).
- A Django `filter(**request.data)` with a foreign key exposes an ORM oracle over any related field, including another user's password.
- A Rails `Hash#merge` with `params.to_unsafe_h` after a `Marshal.dump` is a JSON-injection route to raw `Marshal.load`.

## Traps

- `.ico` is rendered by Chrome as an image, so the cached HTML never runs; use `.html`.
- The report bot must be given the internal `http://127.0.0.1:1337/...` URL, not the public address, or its session is not used.
- The `contract_manager` cookie is HttpOnly; only same-origin actions are available, so the XSS must act inside the page.
- The Marshal gadget needs the detection step first to create the git cache directory, otherwise it raises `Errno::ENOENT`.
- The RCE gadget depends on the exact Ruby/gem build; the same bytes can fail on a patched image.
- Leftover state on a shared instance: created templates were deleted; the `/f.html` file written by the RCE could not be removed and the instance should be reset.
