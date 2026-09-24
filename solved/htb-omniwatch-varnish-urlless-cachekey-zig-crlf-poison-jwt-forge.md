# OmniWatch — SOLVED (self-solved)

- Platform: HackTheBox (web). Varnish 6.5 in front of a Flask controller and a
  Zig `httpz` oracle, MySQL, a Selenium moderator bot, all as root on debian:11.
- Date: 2026-09-23
- Target: `http://154.57.164.83:30264`
- Flag: redacted; rendered by `/controller/admin`, which shells out to `/readflag`
- Source was supplied.

## The bug that makes everything else reachable

`config/cache.vcl`:

```vcl
sub vcl_hash {
    hash_data(req.http.CacheKey);
    return (lookup);
}
```

That is the whole hash function. **The URL is not part of the cache key** — only
one request header is, and it is a header clients choose freely. Two requests to
completely different paths, on different backends, share a cache slot whenever
their `CacheKey` headers match, and a browser that sends none shares the empty
slot with everybody else.

`vcl_recv` then opens the door the rest of the way:

```vcl
if (req.url ~ "^/controller/home"){
    set req.backend_hint = default1;
    if (req.http.Cookie) { return (hash); }     # overrides the builtin pass
}
```

The builtin `vcl_recv` passes anything carrying a `Cookie`. This line overrides
that for exactly the page the logged-in bot lands on, so the bot's authenticated
`/controller/home` is served out of a slot any anonymous visitor can fill.

## Filling the slot: two bugs in the Zig oracle

`oracle/src/main.zig` URL-decodes a path segment straight into a response header
and reflects another into HTML:

```zig
const decodedDeviceId = try std.Uri.unescapeString(allocator, deviceId);
res.header("DeviceId", decodedDeviceId);            // CRLF injection
...
res.body = try std.fmt.allocPrint(res.arena, htmlTemplate, .{ decodedMode, ... });
```

`httpz`'s `res.header()` is `headers.add(name, value)` with no validation, so
`%0d%0a` in the path splits the header block. Varnish only stores a response
when the backend says so:

```vcl
if (beresp.http.CacheKey == "enable") { set beresp.ttl = 10s; }
```

so the injected headers supply exactly that, plus a content type:

```
GET /oracle/<payload>/z%0d%0aCacheKey:%20enable%0d%0aContent-Type:%20text%2fhtml
```

```
DeviceId: z
CacheKey: enable
Content-Type: text/html
Cache-Control: public, max-age=10
```

A following request to `/controller/home`, `/controller/admin` or any oracle URL
answers `X-Cache: HIT` with that body.

## The chain, once the bot renders attacker HTML

1. **Steal the session.** `resp.set_cookie("jwt", jwt, expires=...)` sets no
   `httponly`, so the payload reads `document.cookie`.
2. **Read any file.** `/controller/firmware` does
   `open(os.path.join(os.getcwd(), "application", "firmware", patch))` — an
   absolute `patch` discards the whole prefix, so `/app/jwt_secret.txt` comes
   back verbatim.
3. **Write to the database.** `fetch_device` is
   `f"SELECT * FROM devices WHERE device_id = '{device_id}'"` run with
   `multi=True`, which splits on `;` and commits after every statement.
4. **Forge an administrator.** `administrator_middleware` wants a valid HS256
   token whose last segment equals `signatures.signature` for the token's
   `user_id`. It never checks that the user exists, so the token names
   `user_id: 1337` and the injection inserts that row — an id the bot never logs
   in as, so its next login cannot rotate it away.
5. `/controller/admin` runs `os.popen("/readflag")` and renders the result.

## Traps that cost real time

- **A cache read is destructive.** The custom `vcl_backend_response` sets
  `beresp.ttl = 0s` for anything without `CacheKey: enable`, and Varnish's
  *builtin* `vcl_backend_response` then converts `ttl <= 0` into an
  **uncacheable hit-for-miss object with a 120 second lifetime**. Every poll of
  an empty slot therefore locked that slot for two minutes and swallowed the
  payload's next write. This looked exactly like "the payload never ran".
- **A same-origin `fetch` sends cookies by default, and that alone makes the
  response uncacheable.** `vcl_recv` only sets a backend for `^/oracle` before
  falling through to the builtin, which passes any request with a `Cookie`. The
  beacon returned `200` and `X-Cache: MISS` and was never stored. It worked from
  the cookie-less login page and vanished from the logged-in one — the decisive
  clue. `credentials:'omit'` fixes it.
- **Poisoning too early breaks the bot.** Its first request is
  `GET /controller/login` with no cookie, which lands in the same empty slot, so
  the poisoned page must itself contain a working copy of the login form or
  Selenium never finds `#username`. With the form present the login still
  succeeds and the next navigation runs the payload with a cookie.
- **Two beacons in one time bucket collapse into one.** A slot holding a live
  object turns the next write into a HIT, which stores nothing, so the login
  page's beacon silently ate the home page's.
- **The container clock is not yours.** Slot names derived from `Date.now()`
  need the skew measured from the response `Date` header; a few seconds put the
  write and the read in different buckets.
- **A literal `/` in the injected header value breaks routing**, not the
  injection: `Content-Type: text/html` adds a path segment and the Zig router
  stops matching, answering 404. Encode it as `%2f`. A lone `%0d` without a
  valid following header line gives `503 Backend fetch failed`, which is itself
  proof the injection landed.
- **`crypto.subtle` is undefined outside a secure context.** Doing the HMAC in
  the browser worked on the bot's `http://127.0.0.1:1337` origin but could never
  be rehearsed from anywhere else. Shrinking the payload to "steal the cookie"
  and doing the crypto in Python removed the dependency.
- **Leftover poisoners from earlier attempts keep serving an old payload.** A
  poison request that HITs does not overwrite, so a stale process pins the slot
  and every new version is silently ignored.

## Cleanup performed

A final signed request deleted `signatures` row 1337 through the same injection;
the forged administrator token now redirects to `/controller/login`. The poisoned
objects carried a 10 second TTL and have expired — `/controller/home` answers the
real `302 /controller/login` again.

## Reusable lessons

- **Read `vcl_hash` before anything else.** A cache key that omits the URL turns
  every cacheable response into a response for every URL, across backends.
- **`return (hash)` inside a Cookie branch is always deliberate**, and it is
  always the page whose authenticated content someone wants shared.
- **A response header built from a URL-decoded path segment is header
  injection**, and in a cache stack the header worth injecting is whichever one
  the cache uses to decide storability.
- **When a beacon disappears, suspect the channel before the payload.** Here
  three separate properties of the cache — hit-for-miss on reads, pass on
  cookies, no-overwrite on hits — each made a working payload look dead.
