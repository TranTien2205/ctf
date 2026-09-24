# Spell Orsterra — SOLVED (assisted: writeup named the technique; chain re-derived and improved)

- Platform/event: HackTheBox, University CTF 2022 (author rayhan0x01)
- Target: `154.57.164.82:32071`, source supplied (white-box)
- Stack: PHP 8.1 / Symfony 6.1 / Twig / Doctrine+SQLite / Redis / Symfony Messenger,
  behind nginx -> Apache (mod_php). `APP_ENV=dev`, `APP_SECRET` in `.env`.
- Win condition: RCE. The flag is `/root/flag` and `/root` is `0700`, so arbitrary
  read as `apache` is useless; only the SUID `/readflag` (`chmod 4755`) can read it.
- Flag: verified live via `/readflag`, value intentionally not committed.

## Chain

1. Config before code. `redis.conf` exposes `unixsocket /run/redis/redis.sock`
   with `unixsocketperm 775`; the Dockerfile does `usermod -g www-data redis`, and
   Alpine's nginx user is in `www-data` — so nginx can open the Redis socket.
   `proxy.conf` has `location ~ /assets/(.+)/ { proxy_pass http://$1; }`.
2. SSRF confirmed read-only: `/assets/127.0.0.1:80/` returned the app's own login
   page; `/assets/example.com/` proved outbound egress.
3. Reached Redis with **no external server**: nginx's `proxy_pass` accepts
   `unix:<path>:<uri>` and percent-DECODES the uri, which supplies the literal
   spaces the Redis inline protocol needs. `curl -X EVAL` puts the method in the
   first inline token, so the socket receives
   `EVAL "<lua>" 0 <hex> HTTP/1.0`. The published solution used a VPS returning a
   302 `Location:` header for this; that step is unnecessary.
4. The Lua hex-decodes `ARGV[1]` and `XADD`s it to the `messages` stream. `EVAL`
   still works although `SCRIPT`/`CONFIG`/`FLUSHALL`/`MODULE` are renamed away.
5. Payload = Symfony Messenger envelope. Field is plain
   `json_encode(['body'=>addslashes(serialize($envelope)),'headers'=>[]])`;
   `PhpSerializer::decode()` does `stripslashes()` then `unserialize()`.
   `App\MessageHandler\SubscribeNotificationHandler` is nested as the message's
   `uuid` property so its `__destruct` runs -> `MapExportService::generateMap()`
   -> `imagepng($map, '/www/public/static/exports/'.$export_file)`: arbitrary path,
   PNG content.
6. Getting PHP into a GD-re-encoded PNG: the writeup's Synacktiv IDAT pixel array
   produces nothing on current GD/zlib (the IDAT is a dynamic-Huffman block). Used a
   **palette** PNG instead — `PLTE` is raw and uncompressed, and GD only *appends*
   palette entries — so `<?=` + backtick `$_GET[1]` backtick + `?>` sits verbatim in
   the palette. Handler coords set off-canvas (`9999`) and width 30 make both
   `imagecopymerge` calls no-ops, leaving the palette pristine.
7. `export_file=exploit.php` -> `GET /static/exports/exploit.php?1=/readflag`.
   mod_php echoes the file bytes up to the tag, then the command output, so the flag
   appears immediately after the literal `PLTE` bytes.

## Evidence ancestry

- Deserialization path proven offline against the real Symfony 6.1 `PhpSerializer`
  semantics with stub classes before any traffic.
- nginx -> unix socket -> Redis proven on a local nginx+redis replica built from the
  challenge's own config files; the bytes landing in Redis were byte-identical to intent.
- The GD survival of the PLTE payload proven by replaying `generateMap()`'s exact
  transform chain in `php:8.1.10-alpine3.16` + `php81-gd`, then executing the result.
- Live chain proven with a harmless probe first (map/stamp = the target's own
  `clean_map.png`, unique output name) before any code payload.

## Reusable lessons

- `proxy_pass` to a variable can target a **unix socket**, and nginx percent-decodes
  the uri — that alone converts a proxy SSRF into an arbitrary line-protocol write,
  with no attacker-hosted redirect.
- The write is **blind**: Redis's `Host:`-header guard calls `freeClientAsync`, which
  discards the reply already queued for line 1, so nginx always returns 502. Judge
  success only by an out-of-band observable.
- Confirm a multi-stage deserialization chain with a benign write first; it isolates
  "did the queue injection work" from "does my code payload work".
- Don't trust a published image-polyglot byte array. Re-verify it against the target's
  exact image pipeline; prefer an uncompressed container (`PLTE`) over fighting deflate.
- Local Docker repro of a 2022 handout can be blocked by 2026 tooling (Composer now
  refuses advisory-flagged packages, and there is no `composer.lock`). Replicating only
  the two layers that mattered (GD, and nginx+redis) was far cheaper than the full app.
