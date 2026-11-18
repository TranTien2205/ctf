# Init & Hook Files — the files that execute themselves

## The auto-executed file inventory — write one, get exec

| File | Trigger | Platform |
|---|---|---|
| `~/.bashrc`/`.profile`/`.bash_profile` | next shell login | linux |
| `~/.ssh/authorized_keys` | next ssh attempt | linux |
| `~/.config/autostart/*.desktop` | next desktop session | linux |
| cron.d/crontab lines via file write | cron daemon tick | linux |
| `php.ini` `auto_prepend_file=` | every php request | php |
| `.user.ini` `auto_prepend_file=` | every php request in that dir | php-fpm/cgi |
| `web.config` `httpHandlers`/`httpModules` | next IIS request | iis |
| `.htaccess` `AddHandler`/`SetHandler`/`php_value` | next apache request | apache |
| `~/.gitconfig`/`git hooks` | git operations | any |
| `Makefile`/`Rakefile`/`Taskfile` | build run | any |
| `supervisord` config reload | supervisor restart | linux |
| `systemd` unit file in `~/.config/systemd/user/` | `systemctl --user daemon-reload` + start | linux |
| `init.d`/`rc.local` | boot | linux |
| `composer.json` `scripts` | `composer install` | php |
| `Gemfile`/`.rb` in $LOAD_PATH | `require` | ruby |

## `.user.ini` — the php-fpm per-dir config — the BIG one

PHP-FPM reads `.user.ini` in every dir it serves. Landing one via upload:

```ini
auto_prepend_file=/var/www/uploads/shell.php
```

OR self-referential — the uploaded `.user.ini` + an uploaded php file in
the same dir = auto-prepended exec on EVERY php request in that dir —
even `index.php`. This is the documented HTB/CTF php-fpm shape.

```
uploads/
  .user.ini          → auto_prepend_file=shell.jpg
  shell.jpg          → real jpg? no — any file with <?php works because
                       prepend runs it as code regardless of ext
```

The `.jpg` trick: `auto_prepend_file` runs the file as PHP — the ext
doesn't matter, only the content — so an image-ext filter is bypassed by
`auto_prepend_file=shell.jpg`.

## `.htaccess` — the apache per-dir override — `apache-deep.md` covers
this, but the upload-mechanics version:

- `AddType application/x-httpd-php .jpg` → jpgs exec as php
- `SetHandler application/x-httpd-php` → all files in the dir exec
- `php_value auto_prepend_file /path/shell` → prepend
- `Options +ExecCGI` + `AddHandler cgi-script .x` → cgi

The upload of `.htaccess` itself + one payload file = dir-level handler
override. Whether `.htaccess` is honored depends on `AllowOverride` —
`apache-deep.md`.

## `.bashrc`/`.profile` — needs a shell login

Writing into `~/.bashrc`/`~/.profile`/`~/.zshrc` runs on the next
interactive/login shell — requires the write to land in a home dir AND a
login to happen (the admin's login, a cron that shells in, an ssh
session).

## `~/.ssh/authorized_keys` — direct key insertion

Landing a file into `~/.ssh/authorized_keys` (traversal write) = your
public key becomes valid — persistent access. Requires `~/.ssh` exists
or `StrictModes` tolerance. This is the single most useful traversal
write when it works.

## `auto_prepend_file` in `php.ini` — the global variant

Same mechanism, php.ini level — a php.ini traversal-write = global
prepend.

## The "hook runs on action, not upload" reality

Every entry needs its trigger — a `.bashrc` waits for login, `.htaccess`
waits for the next request to that dir, `auto_prepend` waits for php.
The upload step + the trigger step + the exec — three links to verify.

## Falsifiers

- the write can't reach ANY auto-loaded location (home, ini dirs,
  config paths, hook dirs)
- the trigger never happens (no login, no request to that dir)

## Output to record

- which auto-loaded file is writable + its trigger mechanism
