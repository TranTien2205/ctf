# PHP Sinks — which function reaches a shell and how

## The sink table

| Function | Reaches shell? | Notes |
|---|---|---|
| `system($cmd)` | sh -c | echoes output directly |
| `exec($cmd, &$out, &$ret)` | sh -c | output to array, last-line return |
| `shell_exec($cmd)` | sh -c | returns all output |
| `passthru($cmd)` | sh -c | raw binary output |
| `` `$cmd` `` | sh -c | backtick operator = shell_exec |
| `popen($cmd,'r')` | sh -c | pipe handle |
| `proc_open($cmd,...)` | sh -c unless array | descriptor-spec control |
| `pcntl_exec` | NO shell | replaces image — argv only |
| `eval($code)` | PHP evaluator | PHP code exec — `eval-injection.md` |
| `assert($str)` | PHP evaluator | PHP < 8 string assert |
| `create_function` | PHP evaluator | deprecated 7.2+ |
| `preg_replace /e` | PHP evaluator | e-modifier — removed PHP 5.5+ |
| `include`/`require` on user path | PHP evaluator | file inclusion → RCE |
| `mail($to,$subj,$msg,$hdr)` | sendmail via shell! | `-X`/`-C` flag injection |
| `mb_send_mail` | same | same |
| `imap_mail`/`openssl_pkcs7*` | sendmail | flags surface |
| `move_uploaded_file`/`copy`/`file_put_contents` | filesystem | upload sinks not exec |
| `unserialize` | PHP objects | `web-deserialization` |
| `call_user_func($f,$a)` | PHP function call | `$f`=`system` → exec |
| `array_map($f,...)`/`usort`/`register_shutdown_function` | PHP call | dynamic-callable exec |
| `phpinfo()` etc | no | info |
| `escapeshellarg`/`escapeshellcmd` | sanitizers — see `filter-bypass.md` | |

## The `mail()` sendmail trick — flag injection via 5th arg

```php
mail($to, $subj, $msg, $headers, $params)
```

`$params` appends to the sendmail command line — `-x$v` or `-C$file`:

```
$params = "-X/var/www/html/log.txt"    — sendmail logs to file (write!)
$params = "-C$file"                    — config file
```

If `$params` is user-controlled → write/exec via sendmail flags —
argument-injection into `sendmail`.

## `eval` and friends — the PHP-evaluator sinks

`eval($code)` runs PHP code — payload is PHP not shell:

```php
system('id');           // full function access inside eval
`id`;                   // backticks inside eval = shell_exec
file_get_contents('/flag');
```

`assert('system("id");')` — PHP <8 executes string assert as eval.
`create_function('$x','return system($x);')` — deprecated but exists.

## `preg_replace /e` — legacy but CTF-classic

```php
preg_replace('/.*/e', $_GET['x'], 'x');  — PHP<5.5
```

`/e` evals replacement — direct code exec. Dead on modern PHP but
shows in archived apps.

## `call_user_func` family — dynamic callable

```php
call_user_func($_GET['f'], $_GET['a']);
call_user_func_array($f, $args);
$f = $_GET['f']; $f($_GET['x']);
array_map($_GET['f'], $arr);
usort($arr, $_GET['f']);
```

`?f=system&a=id` — the classic param-driven dispatch. `call_user_func`
accepts `Class::method`/closures too. `array_filter`/`array_map` are the
webshell-dispatch shapes.

## `proc_open` — the bypass-`disable_functions` sink

`disable_functions=system,exec,shell_exec,passthru` — `proc_open` and
`popen` are often NOT disabled — `proc_open('id', $d, $pipes)` runs.

## `FFI`/`ffi` — PHP 7.4+ native call

`FFI::cdef`/`ffi_load` — ffi=dev feature — native code exec. Rarely
enabled; check `ffi.enable`.

## `pcntl_*`/`posix_*` — the process APIs

`pcntl_exec` replaces image (argv), `pcntl_fork`, `posix_spawn` —
the fork+exec family survives `disable_functions` more often than
`system`.

## LD_PRELOAD via `mail()`/`sendmail` chain — the mail() bypass

The `mail()` + `LD_PRELOAD` chain: set `LD_PRELOAD` env + `mail()` spawns
sendmail → the .so loads → bypass `disable_functions`. (The Chankro /
mail-LD_PRELOAD bypass technique.)

## `imap_open`/`Error:` — `imap_open` `rsh`/`ssh` flag — the `-oProxyCommand`-style
CVE-2018-19518 — `imap_open('{x}norsh -oProxyCommand=id','','')` —
sendmail-style flag injection through an IMAP connect.

## `dl()` — extension loading (SAPI-restricted)

`dl('x.so')` loads a PHP extension — SAPI-restricted and often disabled —
but a writable extension_dir + dl() = native exec.

## PHP sink fingerprinting — which function reached the shell

- `system`/`passthru` echo output → output channel works
- `exec` writes to array → output only if the app echoes the array
- `shell_exec`/backticks → output returned to app — visible only if shown
- `popen`/`proc_open` → streamed — output or not per app logic
- `eval`/`call_user_func` → PHP-context — `phpinfo()` probe shows SAPI

## Falsifiers

- argv-only exec (`pcntl_exec`, `execFile`-equivalents) — dead for
  metachars; `argument-injection.md` may still apply
- `disable_functions` covers all shell sinks AND no proc_open/pcntl/
  mail/imap/FFI/dl path AND `safe_mode`-style restrictions block loads

## Output to record

- which sink + its output-capture style + whether `disable_functions`
  is set
