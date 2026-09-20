# nginxatsu (rescue-mission variant) — SOLVED (self-solved)

- Platform: HackTheBox (web). Same app as `solved/nginxatsu.md`, **different intended path**.
- Date: 2026-09-18
- Target supplied: `http://154.57.164.76:30229` (black-box, no source)
- Flag: redacted; verified live in `GET /` as the admin user
- Cost: 6 probes, ~6 minutes. The 2021 chain card matched at 1.0 coverage and
  its first probe **falsified** — see "Why the card's chain did not apply".

## Chain

1. `GET /` → 302 `/auth/login`; nginx, `X-Powered-By: PHP/7.4.12`,
   `laravel_session` + `XSRF-TOKEN` cookies in Laravel's `{"iv","value","mac"}`
   envelope. Login page `<title>` is `nginxatsu`.
2. Register and log in with my own account (`_token` CSRF field required on both
   forms). The dashboard inlines
   `const API_TOKEN = '...'` and `/static/js/main.js` names every endpoint:
   `GET|POST /api/configs?api_token=`, and `GET /config/{id}`.
3. `POST /api/configs` with the form defaults creates a config row; the returned
   id renders at `/config/{id}`, which links **`/storage/<file_name>.conf`**.
   That is the prefix the alias-traversal card is really about.
4. The generated config itself is the disclosure. It contains, verbatim:
   `# We sure hope so that we don't spill any secrets`
   `# within the open directory on /storage`
   followed by `location /storage { autoindex on; }` under `root /www/public`.
   `root`, not `alias` — so there is nothing to traverse; the bug is that the
   directory is simply **listable**.
5. `GET /storage/` returns an autoindex of 51 `.conf` files plus one file that is
   not a config: `v1_db_backup_1604123342.tar.gz`.
6. The archive is a **plain tar despite the `.gz` name** (`tar tf`, not `tar tzf`)
   and holds `database/database.sqlite`: tables `users`, `nginx_configs`,
   `migrations`, `password_resets`, `failed_jobs`. The dump is regenerated at
   instance start, so the `users.api_token` values in it are live.
7. `users.password` is 32 hex characters — **MD5, not Laravel's bcrypt**.
   `hashcat -m 0` against rockyou cracks the admin row
   (`nginxatsu-adm-01@makelarid.es`) in seconds.
8. Log in as that user: the flag is rendered in the page header of `GET /`,
   inside `<p class="nes-text is-success">`.

## Why the card's chain did not apply

`htb-nginxatsu-alias-traversal-appkey-session-forge-blind-sqli` matched this
target at 1.0 signal coverage and 0.95 confidence — same app, same fingerprint —
and its `first_confirming_probe` still falsified. Both of its `all_of`
preconditions are false here:

- **No alias.** `location /storage` uses `root`, so `/storage../.env` resolves to
  `/www/public/storage../.env` and nginx answers its own 404. Six prefix
  variants (`/static..`, `/assets..`, `/css..`, `%2f`-encoded) all failed.
- **The session is never forged.** `order`/`direction`/`sort` as query parameters
  do not change the row order of `GET /api/configs` (13 rows, first id 8,
  identical across all five variants), so there is no reachable `orderBy` sink
  and no boolean oracle. No APP_KEY is needed, and no `.env` is reachable.

The card behaved correctly: it is a candidate, and its probe is what killed it in
two requests. That is the whole point of the probe-before-reuse rule.

## Reusable lessons

- **A config generator prints the server's own config.** The template comments
  survive into the user's output, so generating one config with the defaults is a
  free source read. Read the generated artifact before attacking anything.
- **`root` and `alias` fail differently, and the 404 says which.** An nginx-branded
  404 means the location matched and the file was absent; a framework-branded 404
  means the request fell through to PHP and that prefix is not served by nginx at
  all. That single distinction ended the traversal branch.
- nginx normalises `..` segments before matching a location, so `/storage../../.env`
  collapses to `/.env` and reaches the app, while `/storage../.env` does not.
  Multi-level traversal on an alias prefix is not testable that way.
- **A `.tar.gz` that is not gzipped**: `file` said `POSIX tar archive (GNU)`.
  Check with `file` rather than trusting the extension.
- **A 32-hex password column in a Laravel app is a finding by itself** — the
  framework default is bcrypt, so a hex column means someone replaced the hasher
  with MD5.
