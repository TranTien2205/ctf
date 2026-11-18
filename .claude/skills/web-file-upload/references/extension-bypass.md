# Extension Bypass — every way the filename defeats the filter

## The model — what the filter actually sees

```
filename="X.Y"  →  sanitize()  →  check(ext)  →  store as <dir>/<name>.<ext>
                                                └ serve+exec decided by ext
```

There are four questions, and each maps to a technique family:

1. Which string does the **check** see vs which does the **store/serve** see?
2. Is the check a **blacklist** (block known-bad) or **whitelist** (allow known-good)?
3. Does the check look at the **last** extension, **first**, or **any**?
4. Does the server's **handler mapping** agree with the check's idea of "the extension"?

## Blacklist bypass — the alternate-execution-extension table

### PHP — extensions Apache/FPM will execute

```
.php  .php3  .php4  .php5  .php7  .phtml  .pht  .phps  .phar  .pgif
.inc  (included-by-PHP only)
.php_ (underscore variants some distros map)
```

`pht`/`phtml` are the highest hit-rate alternates — most blacklist authors
only write `php|php3|php4|php5|phtml`. `.phar` additionally triggers
`phar://` deserialization on include.

### IIS / ASP.NET

```
.asp  .aspx  .asa  .cer  .cdx  .ashx  .asmx  .soap  .shtm/.shtml (SSI)
.config (web.config overwrite — its own attack)
```

`shell.aspx;1.jpg` — IIS semicolon truncation: IIS ignores `;...` in the
extension when mapping to a handler, so `.aspx;1.jpg` executes as ASPX
while passing a `jpg` whitelist that splits on `.`.

### JSP / Tomcat / Java

```
.jsp  .jspx  .jsw  .jsv  .jspf  .war (deployed, not executed)
```

`.war` upload to an autodeploy directory = application deployment. If the
app unpacks war/zips to webapps/, a `.war` upload is a full-context shell.

### ColdFusion / Perl / Python / Ruby

```
.cfm  .cfc        # ColdFusion
.pl  .cgi         # CGI-bin
.py  .pyc         # mod_python / cgi
.rb               # mod_ruby / cgi
```

## Whitelist bypass — get a bad extension past a good-extension check

### Double extension — `shell.php.jpg`

Four outcomes, ordered by frequency:

1. check reads **last** ext (`.jpg` → pass), server maps **last** too →
   served as image, dead end
2. check reads last ext, Apache maps **first executable** ext → with
   `AddHandler php5-script .php` + unknown `.jpg` falling through,
   `shell.php.xyz` executes — try `shell.php.aaaa`
3. check reads **first** ext, store/serve uses last → dead both ways
4. check requires **all** exts whitelisted → dead unless a null/traversal
   splits the checked string

`shell.php.xyz` (unknown last ext) is the classic Apache win: Apache walks
extensions right-to-left looking for a handler; unknown ones are skipped,
so `.php` wins. Whitelist that checks only the last ext passes `.xyz`.

### Case variation — `shell.pHp`, `shell.PhP5`, `shell.PHTML`

- Windows/IIS: filesystem + mapping case-insensitive → `.AsPx` executes,
  while a case-sensitive regex whitelist `\.jpg$` still passes `x.pHp`?
  No — whitelist still rejects; case helps vs **blacklist** `php|aspx`
  written without `(?i)` flag, and vs case-sensitive string compares in
  Python/Node validators on a case-insensitive store.
- PHP on Linux: extension map is case-insensitive for handler lookup? Apache
  `AddHandler php .php` matches case-insensitively → `shell.PHP` executes.

### Trailing junk — chars the check strips but the filesystem honors

```
shell.php.          # trailing dot — Windows strips, check may pass or fail
shell.php           # trailing space — Windows strips
shell.php           # trailing tab/newline
shell.php%20.jpg    # encoded space inside the checked name
shell.php..jpg      # double-dot variant
shell.ph.p          # dotted — PHP on Windows still execs? no; Windows strips inner
```

Windows strips trailing dots and spaces from filenames — `shell.php.`
lands as `shell.php`. A whitelist that demands `\.(jpg|png)$` fails it,
but a blacklist `php$` anchored to the raw string also fails — try both
on Windows targets.

### NTFS alternate data streams — `shell.php::$DATA`, `file.jpg:shell.php`

- `file.jpg:shell.php` → Windows writes `shell.php` as an ADS; some save
  paths truncate at `:` → file lands as `file.jpg` or `file`
- `shell.php::$DATA` → stored content equals the ADS payload; IIS may still
  execute it as PHP
- `shell.php::$INDEX_ALLOCATION` → creates a directory entry

### Null byte — mostly dead on modern stacks, try anyway on legacy

```
shell.php%00.jpg     # PHP <5.3.4, some C/Java handling
shell.php\x00.jpg
shell%2Ephp%00.jpg   # encoded both
```

Java `String` keeps `\0` — but `File`/paths reject; Android/older Tomcat had
real bugs. Modern PHP ignores it. Low priority except on vintage stacks.

### IIS 6-era semicolon — `shell.asp;.jpg`

IIS 6 parsed only up to `;` → executes `.asp`. Largely historic but appears
in CTF emulations and old enterprise apps.

## The check-vs-store split — where the two disagree

### Filename vs Content-Type vs sniffed name

The multipart part carries `filename=` AND `Content-Type:` AND the body.
Checks apply to different subsets:

| Check on | Attack |
|---|---|
| `filename` only | keep ext whitelisted, put payload in body — execute via include/phar/LFI |
| extension only | `shell.php` with `Content-Type: image/jpeg` + GIF89a body |
| MIME only | right MIME, any filename |
| magic bytes only | `GIF89a` prefix + payload (polyglot) |
| all three | polyglot with whitelisted ext — pivot to parser/`server-configs.md` |

### The rename race / double check

App checks `filename`, stores under `<uuid>.<checked-ext>` — fine. But some
apps check the uploaded name and store under a **user-supplied path**
(`path`, `dir`, `destination` fields in the same form) → path traversal
wins regardless of extension → `path-traversal.md`.

## Handler-map tricks — make the server execute a whitelisted ext

If the whitelist is airtight (`.jpg` only), the remaining move is making
`.jpg` executable **server-side**:

- `.htaccess` upload first: `AddType application/x-httpd-php .jpg`
  → `server-configs.md`
- `.user.ini` upload (PHP-FPM): `auto_prepend_file` pointing at a second
  uploaded file → `server-configs.md`
- `web.config` upload (IIS): handler mapping `.jpg → asp.dll`
- Nginx misconfig: uploads under a location where `fastcgi_split_path_info`
  passes `x.jpg/x.php` or `x.jpg%00.php` to PHP — try fetching
  `/uploads/x.jpg/.php` and `/uploads/x.jpg%00.php`
- Apache `mod_negotiation` MultiViews: `/uploads/shell` resolves
  `shell.php` without the ext in URL — also `shell.php.x` served as php

## Extension-vs-Content-Type disagreement exploits

- upload `shell.jpg` that is a valid PHP polyglot → whitelist passes,
  content-sniff passes (real image), and if `.jpg` maps to PHP via
  htaccess/misconfig → RCE
- upload `shell.php` with `Content-Type: image/jpeg` — a check that keys
  ONLY on MIME header passes it; if the store keeps the name → RCE

## The "where does it execute" reality check

An executed extension still needs an executed directory:

```
/var/www/html/uploads/   → Apache+PHP: executes
/srv/uploads/ (separate vhost/static) → never executes; LFI/include needed
S3/GCS bucket            → never executes; parser attacks only
```

Check `execution-paths.md` — an accepted shell.ext that can never run is
storage, and the pivot is what READS it.

## Per-server quick table

| Server | Executes | Whitelist-bypass highlights |
|---|---|---|
| Apache+mod_php | php,php3-7,phtml,pht,phar | `.php.xyz`, `.htaccess`, MultiViews |
| Nginx+php-fpm | php (per location) | `x.jpg/.php`, `x.jpg%00.php`, `.user.ini` |
| IIS | asp,aspx,cer,cdx,ashx,soap | `;`, ADS, web.config, trailing dot/space |
| Tomcat | jsp,jspx,war | `.war` autodeploy, `;` old bugs |
| Node | none by ext | ext is irrelevant — content/parser attacks |

## Probe sequence

```
1. marker.txt upload        → lands? where?
2. marker.php               → rejected? which layer?
3. marker.phtml / .pht / .phar → blacklist gap?
4. marker.php.jpg / .jpg.php → which ext does the check read?
5. marker.PhP / .PHP5       → case sensitivity?
6. marker.php%00.jpg / .php. / "php " → string-split games?
7. GIF89a+php body as .jpg   → is .jpg ever executed? (needs config/misconfig)
8. .htaccess or .user.ini   → can I change the mapping itself?
```

Record which specific arm produced the anomalous accept — that is the
bypass the rest of the chain hangs on.

## Falsifiers

- every extension variant lands on storage that never executes (separate
  static host/bucket, `engine off`, force-download)
- whitelist reads the real stored name AND mapping is airtight AND no
  config-file upload is accepted
- the checked string and the stored string are always identical

## Output to record

- the exact filename that passed + the layer it defeated
- stored name vs sent name (rename pattern)
- fetch URL + whether it executed (verbatim source vs run output)
