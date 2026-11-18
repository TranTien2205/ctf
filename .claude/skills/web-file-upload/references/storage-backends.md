# Storage Backends — where the bytes actually land and what each implies

## The backend decides the exploit path

```
local fs docroot        → exec-by-serve
local fs non-webroot    → include/consumer only
NFS/shared mount        → same as local + multi-server path confusion
S3/GCS/Azure object     → no exec; presigned/policy tricks
DB blob                 → re-served by an endpoint — type decided by app
memory/tmp queue        → processing only
CDN fronted storage     → serve context differs from app
```

## Local filesystem — the classic

- inside docroot → exec/serve angles (`apache-deep`, `nginx-deep`)
- outside docroot → include/phar/template angles (`execution-paths`)
- tmp dirs (`/tmp`, `sys_get_temp_dir`) — world-readable on multi-tenant?
  race angles
- sticky dirs — `/tmp` sticky bit — can't delete others' files but
  overwrite-not-owned fails

## NFS / shared mounts — the multi-server trap

Upload on web-1, fetch on web-2 — the file IS there (shared mount) but
propagation lag or mount differences create windows. Also: the worker
host may mount the same dir — a file "unreachable by URL" on web may be
readable by a worker.

## Object storage (S3/GCS/Azure) — `cloud-storage.md`

- never executes — the only attacks are policy/serve-side or consumer-side
- `s3://`/`gs://` paths appear in source — the fetch is a signed URL

## DB blob storage — `files` table

- re-served by `/download?id=` or `/file/<uuid>` — the endpoint sets
  Content-Type from the stored mime field — a stored `text/html` upload
  serves back `text/html` → stored XSS on app origin
- the stored `content_type` column is a claim — check what the serve
  endpoint emits

## CDN-fronted storage — the double-serve problem

- the app's `/uploads/x` → CDN caches and serves — the CDN's response
  headers decide `nosniff`/`attachment`, not the app's
- cache key tricks — poison the CDN copy (`web-cache-poisoning` class)
- purge/refresh — your file's old version may persist after re-upload

## In-memory/queue — no persistence at all

- file goes to a worker queue — never lands on disk — process-only
- stream-to-processor — the "upload" is a memory stream; no path ever
  exists → consumer attacks only

## The read-back channel per backend

| Backend | How the file is read |
|---|---|
| local | direct URL fetch |
| S3 | presigned GET, CDN URL, app proxy (`/download`) |
| GCS | signed URL, `storage.googleapis.com` |
| Azure | SAS URL |
| DB | `/download?id`, `/file/<uuid>`, inline `<img src=data:>` |
| tmpfs | no read — process only |

## The serve-endpoint shapes — when it's a script not a file

- `/download.php?f=x` / `/file.php?path=` — PHP readfile wrappers —
  the `path` arg is ALSO a wrapper/LFI target (`phpwrappers-upload.md`)
- `/download/<uuid>` streaming endpoint — maps uuid→path server-side
- `X-Accel-Redirect`/`X-Sendfile` responses — the file is served by the
  web server but only after the app's auth check

## Permissions — the write/exec boundary

- `chmod` on save — apps that chmod 777/755+ — a `.sh` upload becomes
  executable? No — the file needs a CGI/handler mapping; 755 alone doesn't
  exec via HTTP. But `cgi-bin` dirs DO honor exec bits.
- ownership — writes as `www-data`/`app` user — `~/.ssh` of the app user
  may be writable
- umask — default file perms

## The "the dir is different from where you think" check

- the app says `uploads/` but the FS is `/var/lib/app/data/uploads/` —
  traversal depth counts differ — the whitebox sink path is the truth
- symlinked upload dir — `uploads` → `/srv/data` — traversal relative to
  the REAL dir, not the URL path

## Falsifiers

- the backend is object storage with private ACLs + no consumer
- the serve endpoint forces `attachment`/`octet-stream` unconditionally
  and no consumer/parser exists

## Output to record

- the backend identified + how the stored file is read back
- the serve-side posture on that backend (types, disposition, origin)
