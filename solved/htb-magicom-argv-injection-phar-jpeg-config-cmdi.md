# Magicom — SOLVED (writeup-assisted)

- Platform: HackTheBox, **Business CTF 2024**, web, rated Medium.
- Date: 2026-09-19
- Target supplied: `154.57.164.82:30726` (black-box at first; official source found mid-solve)
- Second port `154.57.164.82:30658` was supplied as "the same target" but is **not part of
  this challenge** — see the note at the end.
- Stack: nginx → PHP 8.1.28 FPM/FastCGI, MySQL on loopback, imagick loaded, doc root `/www`
- Flag: redacted; read from a live response body
- Assistance: `tools/writeup_search.py` used after `/info` leaked the challenge name. HTB
  publishes the official solver for this event, and it supplied the `gen.php` stub layout and
  the trigger URL. Recorded here as required.

## Chain

### 1. Recon — the 404 page is a front controller, and `common.txt` is enough

`/`, `/home`, `/product`, `/addProduct` are clean URLs with no `.php`, and `/index.php` 404s
through the app's own template: a front controller. `ffuf` with **`common.txt`** (4.7k, not
the big list) returns everything that matters:

```
assets  controllers  home  info  models  product  static  uploads  views
```

`/controllers`, `/models`, `/views` answer `301` with
`Location: http://<host>:1337/...`, which leaks the internal port. **`/info` is a full
`phpinfo()`.**

### 2. `/info` is the whole map

| Directive | Value | Why it matters |
|---|---|---|
| `register_argc_argv` | **On** | this is the enabling misconfiguration — see step 4 |
| `disable_functions` | *no value* | `passthru` is available |
| `open_basedir` | *no value* | `phar://` can point anywhere |
| `allow_url_include` / `allow_url_fopen` | Off | no remote include; the phar must be uploaded |
| `phar.readonly` | On | cannot *create* a phar server-side, but reading one is unaffected |
| `$_SERVER['DOCUMENT_ROOT']` | `/www` | gives the absolute path for the `phar://` URL |
| extensions | **imagick**, phar, dom, mysqli | |
| `System` | `ng-1357854-**webmagicombiz2024**-3xxye-…` | **the hostname leaks challenge and event** |

That hostname is what turned a black-box into a white-box: challenge `magicom`, event
`biz2024`. HTB publishes `business-ctf-2024` on GitHub, and
`web/[Medium] Magicom/htb/` carries `gen.php` and `solve.py` — the official solver.

### 3. The upload accepts a phar, because a phar can start with a JPEG

`/addProduct` takes `title`, `description`, `image` (multipart). Measured behaviour:

| Uploaded | Result |
|---|---|
| 6-byte `GIF89a` header | `Not a valid image.` |
| **valid** 1×1 GIF, valid 1×1 PNG | `Not a valid image.` |
| valid JPEG magic + 200 bytes of junk | `Not a valid image.` |
| valid JPEG renamed `.php` / `.phar` | `Not a valid image.` |
| valid GIF renamed `.jpg` | `Not a valid image.` |
| **valid JPEG with `<?php … ?>` appended** | **`Product added successfully.`** |

So there are two independent checks — a **real image parse** (not magic bytes: JPEG-magic +
junk is rejected) and an **extension whitelist** — but **trailing bytes are preserved**. The
file is then stored as `/www/uploads/<16 hex>.jpeg`, random name, forced extension, served
back as `image/jpeg` and never executed.

That last row is the whole point. `Phar::setStub()` lets the stub be anything ending in
`__HALT_COMPILER(); ?>`, so a **complete valid JPEG can be the stub**:

```php
$phar->addFromString("test.conf", $content);
$phar->setStub($jpeg_header_bytes . " __HALT_COMPILER(); ?>");
```

`file` reports `JPEG image data, … 10x10`, the upload validator agrees, and the same bytes are
still a readable phar archive. Note `gen.php` must run with `php -d phar.readonly=0`
**locally** — the target's `phar.readonly=On` only blocks creation, not reading.

### 4. `/cli/cli.php` — a CLI-only script reachable over HTTP

```php
if (!isset($_SERVER['argv'], $_SERVER['argc']) || !$_SERVER['argc']) {
    die("This script must be run from the command line!");
}
```

and a plain `GET /cli/cli.php` does print exactly that. But with `register_argc_argv = On`,
PHP populates `$_SERVER['argv']` **from the query string** whenever that query string
contains no `=` — splitting it on `+`. So:

```
/cli/cli.php?+-m+import+-c+<path>+-f+/etc/hostname
```

is read by the script as `argv = ['-m','import','-c','<path>','-f','/etc/hostname']`, the
gate passes, and `getCommandLineValue()` hands back attacker-controlled values.

### 5. `-c` is loaded through a stream wrapper, so it accepts `phar://`

```php
$configFilename = isConfig(getCommandLineValue("--config", "-c"));   // file_exists / is_dir
$dbConfig = new DOMDocument();
$dbConfig->load($configFilename);                                     // stream wrappers honoured
foreach ($var->query('/config/db[@name="'.$name.'"]') as $var) { return $var->getAttribute('value'); }
```

`file_exists()`, `is_dir()` and `DOMDocument::load()` all understand `phar://`, so
`-c phar:///www/uploads/<hex>.jpeg/test.conf` reads the XML **out of the uploaded image**.

### 6. The config value lands in a shell string

```php
function import($filename, $username, $password, $database) {
    passthruOrFail("mysql -u$username -p$password $database < $filename");
}
```

`$database` is the `value` attribute from that XML. Setting it to `magicom; /readflag #`
produces

```
mysql -uroot -prootganteng magicom; /readflag # < /etc/hostname
```

`passthru` prints the output straight into the HTTP response. `-f` only has to name a file
that passes `file_exists()` (`/etc/hostname` does) — it is commented out by the `#` anyway.

### 7. Root

`/` contains `-rwsr-xr-x 1 root root 16008 readflag` — setuid root, the standard HTB flag
reader. Running it as `www-data` (`uid=33`) printed the flag into the response body.

## Traps that cost time

- **The injected command is pasted raw into an XML attribute, so `"`, `<` and `&` break the
  whole chain — silently.** `gen.php` does no escaping and `cli.php` parses with
  `DOMDocument`, so a malformed document yields no config, no command, and an **empty 200
  response** that looks exactly like "the exploit stopped working". `2>&1` was what bit me;
  `2>/dev/null` and `2>/tmp/e; cat /tmp/e` are the safe forms. Likewise `mysql -e "select …"`
  must be written `-e select\ id,title\ from\ products`.
- **`mysql` inside the container needs `-h 127.0.0.1`.** Without it the client tries a unix
  socket that does not exist and exits 1 with no output if stderr is discarded.
- **`root` / `rootganteng` in the official `gen.php` is a decoy.** Those credentials are
  invalid on the target; it does not matter, because the first `mysql` command is *supposed*
  to fail — everything after the `;` runs regardless.
- **Do not go looking for a way to execute the uploaded `.jpeg`.** It is renamed to random
  hex, the extension is forced, and nginx serves it as `image/jpeg`. The file is a *data*
  file read through `phar://`, never a script.
- A 6-byte `GIF89a` is not "a valid image" to `getimagesize`. Build real images before
  concluding anything about which formats are accepted.

## Reusable lessons

- **`phpinfo()` in a CTF is the challenge map, and the `System` row is the best single line
  in it.** The kernel hostname carried `webmagicom` + `biz2024`, which named the challenge
  and the event and led straight to HTB's published source. Read the hostname before the
  directives.
- **`register_argc_argv = On` turns every "CLI-only" PHP script into an HTTP endpoint.** The
  check `isset($_SERVER['argv'])` is not an authorisation boundary. The trigger is a query
  string with **no `=` sign**; `+` becomes the argument separator.
- **A phar's stub can be a whole valid image.** Any upload filter that demands a real,
  parseable image and still preserves the file can be fed a phar. The filter is not wrong
  about the file being an image — it is simultaneously both.
- **`phar://` does not need `unserialize()`.** Here no object is deserialised at all: the
  archive is just a way to smuggle an attacker-controlled *file* into a path the application
  will `DOMDocument::load()`. Any `file_exists`/`is_dir`/loader taking a path is a sink.
- Chain the three cheap questions in order: what does the upload keep, what reads a path, and
  what reaches a shell.

## About the second port

`30658` was supplied alongside `30726` as "one target". It is not HTTP (resets on a request
line, no banner, `nmap -sV` reports `unknown`), and once RCE was available, `ss -ltn` inside
the container showed it listens on **only** `0.0.0.0:1337` (nginx), `127.0.0.1:3306` (MySQL)
and `*:9000` (php-fpm). Nothing there maps to `30658`, and the challenge was solved without
it. Treat it as a separate instance rather than a second component of this one.

## Cleanup

`/www/uploads` was emptied of every file the probes created. The matching `products` rows
**could not** be removed: the application's MySQL user `beluga` holds
`GRANT SELECT, INSERT, UPDATE` and no `DELETE`, and no working administrative credential
exists inside the container. The rows remain with titles `probe` / `pm_*` / `T_*` and now
point at deleted images. Seeded rows 1–6 (`/assets/image/…`) were not touched.
