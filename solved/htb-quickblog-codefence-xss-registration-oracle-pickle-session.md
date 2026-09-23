# QuickBlog — SOLVED (self-solved)

- Platform: HackTheBox (web). CherryPy 18 + a client-side markdown renderer,
  Selenium/Chromium admin bot, python:3.11-alpine, supervisord.
- Date: 2026-09-23
- Target: `http://154.57.164.73:32540`
- Flag: redacted; read from `/uploads/res.txt` in a live response
- Source was supplied.

## The chain

Stored XSS in a client-side renderer → steal the admin bot's session id through
the only unguarded write endpoint → arbitrary file write as admin → pickle
deserialisation in CherryPy's file session store → RCE → `/readflag`.

## 1. The XSS sink

`app.js` does `contentDiv.textContent = atob(data.content)` and then
`contentDiv.innerHTML = markdownToHtml(contentDiv.textContent)`, so the sink is
in the browser, not in the server template. `static/js/markdown2html.js`:

```js
// line 7   escapes '<' only — '>' is never touched
markdown.slice(0, start) + '&lt;' + ...
// line 168 the fence language is lowercased
codeLanguage = (line.slice(3) == '') ? 'plain' : line.slice(3).toLowerCase();
// line 173 and then interpolated into an attribute with no quote escaping
`<pre language='${codeLanguage}'><code id='${uuid}'>...`
```

Two constraints follow, and both shape the payload:

- **No new tag can be opened**, because `<` is escaped. So the handler has to
  fire by itself: `autofocus` plus `tabindex` makes the `<pre>` focusable and
  `onfocus` fires the moment it is inserted.
- **Everything is lowercased**, which destroys `toLowerCase`, `Math`,
  `parseInt` and every uppercase byte in a literal. The real payload therefore
  travels percent-encoded and is rebuilt at runtime with
  `eval(unescape("%xx.."))` — both names are already lowercase, and CSP allows
  `'unsafe-inline'` and `'unsafe-eval'`.

```
```x' onfocus='eval(unescape("%76%61%72..."))' autofocus tabindex='1
```

`new_post` also runs `validate_input(title)` (`^[a-z_]+$`), so the payload has
to go in `content`, which is base64 and unchecked.

## 2. Getting the session id back out

The container sets `http_proxy=http://127.0.0.1:9999` — a dead port — so there
is no outbound traffic, and CSP pins `connect-src 'self'`. The id has to come
back *through the application*.

Every write endpoint refuses requests from `127.0.0.1`:

```python
remote_addr = cherrypy.request.remote.ip
if remote_addr in ['127.0.0.1', '::1']: ...   # new_post, upload_file
```

`/register` has **no such guard**. So the bot encodes its own cookie as
registrations, one username per nibble (`w` + position letters + `_` + value
letter — usernames are `^[a-z_]+$`, so digits are mapped to `a..p`), and the id
is read back afterwards with the existence oracle:

```python
if validate_input(username) and username not in users:   # free  -> 303 to /
    ...
raise cherrypy.HTTPRedirect('/register')                 # taken -> 303 to /register
```

`credentials:"omit"` matters: `/register` overwrites
`cherrypy.session['username']`, so reusing the bot's own session would demote it
from admin and destroy the cookie being stolen.

## 3. The trap that cost a whole run

`bot_runner` logs in from scratch **every minute**, so every visit carries a
*different* session id. The first version had no lock, so each run wrote its own
nibbles into the same 40 names and first-writer-wins made the recovered value a
per-position minimum across runs:

```
64a622144421919117143020805124346a224251   <- not any real id
```

The giveaway was the distribution: a random id is uniform over `0-f`, and this
was almost entirely low nibbles. `/admin` answered 303.

The fix is a **lock**: the payload claims one name first and only writes the id
if it created it.

```js
r("wlock_lock", function (q) {
  if (q.url.indexOf("register") > 0) { return; }   // someone else already wrote
  for (var i = 0; i < 40; i++) { ... }
});
```

`fetch` follows the redirect, so `q.url` is the final URL and the oracle is
readable same-origin. With the lock, exactly one bot run writes, and the
recovered id authenticated on the first try.

## 4. Admin → RCE

`admin_user` cannot be hijacked at the account level — `register` checks
`username not in users` — so the stolen cookie is the only way in. With it,
`upload_file` joins the multipart filename unsanitised:

```python
upload_path = os.path.join(uploads_dir, file.filename)
```

CherryPy does not touch the filename (`_cpreqbody` only strips surrounding
quotes), so `../sessions/session-<id>` lands in the session store — and
CherryPy's `FileSession` loads those with **pickle**:

```python
# cherrypy/lib/sessions.py
f = os.path.join(self.storage_path, self.SESSION_PREFIX + self.id)
return pickle.load(f)
```

Setting that cookie and requesting any page runs the payload. `FileSession`
expects `(data, expiration_time)`, so pickling the tuple rather than the bare
object keeps the session machinery from raising afterwards:

```python
pickle.dumps((RCE(cmd), time.time() + 86400), protocol=2)   # __reduce__ -> os.system
```

`entrypoint.sh` renames the flag to `/flag<10 hex>.txt`, so it has to be
globbed; `/readflag` is setuid root and does it. The output goes to
`/app/uploads/`, which is a `staticdir` with no auth.

## Traps that cost real time

- **A bot that re-authenticates on a schedule has no stable session id.** Any
  multi-request exfil through a shared namespace silently mixes runs. Lock the
  namespace to one run, or the result is a plausible-looking value that is not
  any real id.
- **Nibble distribution is a free correctness check.** A recovered secret that
  is not uniform over its alphabet was assembled wrongly; that was visible
  before the cookie was ever tested.
- **The existence oracle writes.** Probing a name registers it, so probing
  *before* the bot has run hands it a name it can no longer create and that
  nibble is lost for good. The lock name especially must never be probed.
- **`{`Content-Type`: ...}` is a SyntaxError** — a template literal cannot be an
  object key. The percent-encoding already makes ordinary double quotes safe.
- **`http.server` is single-threaded**, and headless Chrome opens several
  connections, so the local rehearsal deadlocked until it became
  `ThreadingHTTPServer`. Same trap as Venzenulon.

## Cleanup performed

The planted session file is a working RCE for anyone who sets that cookie, so
the command removes it as its last act (`rm -f /app/sessions/session-<id>*` —
unlinking it while `pickle.load` still holds it open is fine on Linux). A second
run deleted `/uploads/res.txt`. Re-triggering both planted cookies afterwards
produced nothing and `/uploads/res.txt` returns 404. The throwaway accounts and
the two payload posts live only in the process's memory; there is no delete
endpoint, and forcing a restart was not worth killing the instance over.

## Reusable lessons

- **When `<` is escaped but `>` is not, look for an attribute sink and an
  auto-firing handler.** `autofocus` + `tabindex` turns any element into one.
- **A lowercasing filter is not a filter.** `eval(unescape("%xx"))` is entirely
  lowercase and reconstitutes arbitrary case at runtime.
- **When egress is blocked, the app's own write endpoints are the channel.**
  Enumerate which ones carry the localhost guard; the one that does not is the
  exfil path, and a "user already exists" redirect is a one-bit read.
- **Any framework session store that pickles is a write-to-RCE conversion.**
  CherryPy's `FileSession` turns one arbitrary file write into code execution
  with no memory-layout work at all.
