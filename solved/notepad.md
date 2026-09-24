# notepad (picoMini by redpwn) — web

Flag read from a live response. Value not recorded here.

## Chain
`/new` rejects `_` and `/` in content, then writes to
`static/{url_fix(content[:128])}-{token_urlsafe(8)}.html`.

werkzeug's `url_fix` begins with:

    s = _to_str(s, charset, "replace").replace("\\", "/")

It rewrites **backslashes to slashes after the app's check has passed**, so
`..\templates\errors\` becomes `../templates/errors/` and the write escapes into
`/app/templates/errors/` — which the Dockerfile makes world-writable
(`chmod 1773 static templates/errors`).

`index.html` does `{% include "errors/" + error + ".html" %}` with `error` straight
from the query string, so the planted file is **rendered as a Jinja template**.

## Traps
- The filename is `content[:128]` but the file receives the FULL content: pad the
  first 128 bytes to the traversal path so the payload can't pollute the name.
- The payload must ALSO avoid `_` and `/`, which kills every `__class__`/`__globals__`
  chain. Smuggle the dunders through `request.args` (jinja getattr falls back to item
  lookup, so `request.args.g` is the `g` query param) and parameterise module and
  callables so you can pivot from the URL instead of planting another file.
- `cycler.__init__.__globals__` is `jinja2.utils` and has no `os`; `lipsum` does.
