# Wayback Machine and public caches

Deleted content persists: the Wayback Machine, Google cache, and archive.today hold the endpoint's history — a CTF-legitimate source when the artifact used to be public.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| challenge history on archive.org | old versions | read removed routes |
| deleted page in Google cache | cached content | read the snapshot |
| old robots.txt in wayback | historical hidden paths | probe current state |

## Steps

1. Query web.archive.org for the target's path snapshots.
2. Historical .env/backups/routes sometimes persist in snapshots even after removal.
3. Use it to learn the app's structure, then probe live for current artifacts.
4. Record that the wayback source was used (it's untrusted-but-legitimate history).

## Falsifier

Falsifier — no snapshots or the artifact never was public: channel empty.

## Traps

- Wayback content is historical — a found secret may be rotated; verify live.
- Some CTFs consider external archives out-of-scope — check the rules.
- The archive itself is a search: web.archive.org/web/*/url, not a probe of the target.

## Commands

```bash
curl -s 'http://archive.org/wayback/available?url=target'
```

## Cross-references

`bounded-sweep.md`
