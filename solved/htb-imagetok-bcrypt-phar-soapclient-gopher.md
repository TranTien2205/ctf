# ImageTok — SOLVED (one detail writeup-assisted)

- Platform: HackTheBox (author makelaris). Target: `154.57.164.64:31613`, source supplied.
- Stack: nginx + php-fpm 7.4.10, custom MVC, MariaDB, php7-phar + php7-soap,
  curl **7.70.0 compiled from source** on purpose.
- Flag: lives in a MySQL table the app never reads; recovered into the attacker's own
  session cookie. Value not committed.

## Why each defence fell

1. **Session forgery — bcrypt truncates at 72 bytes.** The cookie is
   `base64(json).base64(password_hash(SECRET.$json))` verified with
   `password_verify(SECRET.$data, $sig)`. `entrypoint.sh` makes SECRET 15 chars, so only
   `json[0:57]` is ever hashed. `CustomSessionHandler::toJson()` does `ksort`, putting
   `files` before `username` — so uploading images pads `files` until `username` sits
   past the boundary and can be rewritten to `admin` while keeping the original
   signature. Two uploads is enough (offset 63). Verified offline on PHP 7.4 before
   touching the target. One accepted forgery is permanent: the app immediately re-saves
   and re-signs `{"files":[],"username":"admin"}`.
2. **DB creds — `/info` is `phpinfo()`.** `DB_NAME`, `DB_USER` come from
   `fastcgi_param`, and `DB_PASS` is empty.
3. **`/proxy` gate.** Needs `username=='admin'` (done), `Host: admin.imagetok.htb`
   (an nginx rule), and `REMOTE_ADDR=='127.0.0.1'` — confirmed genuine live
   (`/api/bot/login`-style 401 "Your IP is not allowed"), so the request has to
   originate inside the container.
4. **Getting inside — phar + SoapClient.** `FileModel::__construct` does
   `urldecode($file_name)`, and `/image/{param}` reaches `file_exists()`, so
   `phar://` triggers metadata deserialization. The only gadget needed is
   `ImageModel::__destruct`, which calls `$this->file->getFileName()`; setting `file`
   to a **SoapClient** turns that into `SoapClient::__call` → an outbound HTTP request.
   A CRLF-stuffed `user_agent` smuggles a complete second request (Host, admin Cookie,
   Content-Type, Content-Length, body) down the same keep-alive connection. The first
   request eats nginx's 403; the smuggled one is the real `POST /proxy`.
5. **Scheme allowlist — `parse_url` vs curl.** The gate only inspects the URL when
   `parse_url` returns something. `gopher:///127.0.0.1:3306/_...` (three slashes) makes
   `parse_url` return `false` for scheme, host **and** port, so all three `!empty()`
   guards short-circuit — while curl still connects. Four slashes fails.
6. **Why curl 7.70.0 is pinned.** A MySQL handshake is full of NUL bytes. curl 7.74
   rejects `%00` in a URL (errno 3, URL_MALFORMAT); **7.70.0 accepts it.** Tested both
   side by side. Without the old curl this whole path is dead.
7. **Exfil with no output channel.** The proxy's response goes back to the SoapClient
   and is discarded, so the chain is blind. But the DB user holds
   `INSERT ON *.*`, and the app serialises `files` into the client's cookie — so
   `INSERT INTO <db>.files(...) SELECT flag,"1","flag" FROM <db>.definitely_not_a_flag`
   makes the flag appear in the cookie of whoever is called `flag`.

## Evidence ancestry

Everything except the live target was proven offline first, while the instance was down:
bcrypt forgery on PHP 7.4; the `gopher:///` gate bypass on PHP 7.4 + curl; the `%00`
difference between curl 7.70.0 and 7.74; the MySQL packet driven against a real MariaDB
with the challenge's schema and grants (the INSERT landed); the phar/PNG polyglot
passing `mime_content_type` + `getimagesize`; and the SoapClient gadget, captured as raw
bytes on a listener showing the smuggled `POST /proxy`.

## Reusable lessons

- Any `bcrypt(secret . data)` signature has an unsigned tail once the input passes 72
  bytes. Look at what orders the fields — here `ksort` decided which one was protected.
- `scheme:///host:port/path` is a clean `parse_url`/client split: PHP sees nothing,
  the HTTP client still connects.
- Pin-pointing a *deliberately old dependency* in a Dockerfile is a hint. curl 7.70.0
  was there for one reason: `%00` in URLs.
- A `__destruct` that calls any method on a property is enough for SSRF when
  ext-soap is present — SoapClient's `__call` is a universal "method → HTTP request"
  adapter, and `user_agent` is a CRLF header-injection sink.
- **PHP urldecodes the POST body.** A percent-encoded payload passed in a form field
  must be double-encoded (`%` -> `%25`). This was the only defect in the first live run:
  the chain executed perfectly and inserted nothing, because `$_POST['url']` had been
  decoded to raw bytes.
- When a blind SSRF has no reply channel, look for a write primitive plus anything the
  app already serialises back to you. INSERT + a session cookie is a read channel.
