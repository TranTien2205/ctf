# Recon order — where the map sits in the broader pass

## The layered recon

The map is one recon layer among several — a lax deployment ships more
than the map. The order, by yield:

```
1. entry page       -> the script inventory, __NEXT_DATA__, SPA marker
2. manifests        -> _buildManifest / asset-manifest / sw.js precache
3. the map          -> .map recovery -> sourcesContent -> real source
4. the bundle       -> string mine every chunk (endpoints/secrets/flags)
5. .git             -> /.git/HEAD -> git-dump the server source
6. .env / config    -> /.env, /config.js, /env.js, /settings.json
7. backups          -> /backup.zip, /app.zip, /db.sql, /src.tar.gz
8. source paths     -> /src/config/x.js, /static/src/y.js
9. robots/sitemap   -> /robots.txt, /sitemap.xml (the hidden route list)
10. web-triage      -> the broader recon/classification layer
```

## Why this order

- the entry page + manifests give the *complete* asset+route inventory
  cheaply — enumerate before mining
- the map gives the *real source* — the highest single-file yield
- the bundle strings give the *endpoint/secret* surface — the lead list
- `.git`/`.env`/backups give the *server* source + credentials — the
  bigger leak on a lax host

## The map's place

The map is the *client-source* layer — it recovers what the server
shipped to the client. `.git`/`.env` are the *server-source* layer —
they recover what the server did not mean to ship. Probe both; the map
is the signal the deployment is lax.

## The handoff

Each layer feeds the next — the map names the surface; the `.git`
recovers the server source that explains it; `web-triage` classifies
the found endpoint; the class skill exploits it. The map is the front
door; the others are the rest of the unlocked house.

## The bounded pass

The whole recon is bounded — one entry fetch, the manifest probes, one
`bundle_miner`, the disclosure probes, one verify pass. Do not spend
the challenge budget re-mining; route each find and work the class.
