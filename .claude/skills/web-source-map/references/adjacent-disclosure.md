# Adjacent disclosure — the deployment that ships its map ships more

## The lax-deployment signal

A host that ships a `.map` (or a dev bundle, or `__NEXT_DATA__` with
config) signals a lax deployment — the build's debug artifacts are
public. The same laxness usually exposes `.git`, `.env`, backups, and
static source.

## The disclosure probe order

After the map, probe the adjacent disclosure surface — ordered by yield:

```bash
# the classic sequence on a host that ships .map
for p in /.git/HEAD /.env /.git/config /backup.zip /src/config/secrets.js \
         /static/maps/ /config.js /env.js /api/config /.DS_Store \
         /package.json /composer.json /README.md /CHANGELOG.md \
         /.gitignore /web.config /robots.txt /sitemap.xml; do
  printf '%-30s ' "$p"
  curl -s -o /dev/null -w '%{http_code} %{content_type}\n' "$BASE$p"
done
```

## The `.git` check — the big one

`/.git/HEAD` returning `ref:` → a readable git repo → `git-dumper` or a
manual object walk recovers the *entire* source history — far richer
than a `.map`. The `.map` is the client's shipped source; the `.git` is
the server's.

```bash
curl -s "$BASE/.git/HEAD"
# -> 'ref: refs/heads/main' means .git is public — recover the tree
```

## The `.env` check

`/.env` returning `KEY=VALUE` lines → the server env file — database
credentials, app secrets, API keys. Higher value than most map finds.

## The backup/archive check

`/backup.zip`, `/app.zip`, `/src.tar.gz`, `/www.zip`, `/db.sql`,
`/dump.sql` — a packaged source/db the deployment left.

## The config/script check

`/config.js`, `/env.js`, `/settings.json`, `/manifest.json`,
`/config.json` — a runtime config file, separate from the bundle.

## The robots/sitemap check

`/robots.txt` and `/sitemap.xml` name routes the owner wants hidden —
a free route list that complements the bundle's.

## The routing note

Each adjacent find routes to its own class — `.git` →
`web-info-disclosure`/`file-read-primitives`, `.env` →
`web-info-disclosure`, a readable source file → the source's own class.
The map is one door; the adjacent surface is the rest of the unlocked
house.
