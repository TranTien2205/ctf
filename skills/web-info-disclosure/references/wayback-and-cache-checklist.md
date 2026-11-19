# Wayback Machine and public caches — checklist

Deleted content persists: the Wayback Machine, Google cache, and archive.today hold the endpoint's history — a CTF-legitimate source when the artifact used to be public.

## Checklist

- [ ] Query web.archive.org for the target's path snapshots.
- [ ] Historical .env/backups/routes sometimes persist in snapshots even after removal.
- [ ] Use it to learn the app's structure, then probe live for current artifacts.
- [ ] Record that the wayback source was used (it's untrusted-but-legitimate history).

## Abort conditions

- Wayback content is historical — a found secret may be rotated; verify live.
- Some CTFs consider external archives out-of-scope — check the rules.
- The archive itself is a search: web.archive.org/web/*/url, not a probe of the target.

## Falsifier

Falsifier — no snapshots or the artifact never was public: channel empty.
