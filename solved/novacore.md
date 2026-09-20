# NovaCore — SOLVED (assisted: official writeup + official solver)

- Platform: HTB Business (Global Cyber Skills Benchmark) CTF 2025 — "A Never-ending Chain", ~20 solves
- Date: 2026-09-07
- Flag: `HTB{REDACTED}`
- Artifacts: `~/ctf/challenges/novacore/solver.py` (official solver, patched HOST/PORT + tool check)
- Writeup used: blog.elmosalamy.com "Novacore: A Never-ending Chain" + hackthebox/business-ctf-2025 official repo
- Fingerprint → `tools/writeup_search.py "NovaCore HTB"` → instant hit (first query)

## Chain (10 vulns, in order)

1. **Traefik v2.10.4 CVE-2024-45410**: hop-by-hop header removal —
   `Connection: close, X-Real-Ip` strips Traefik's `X-Real-Ip` → Flask's
   `token_required` treats headerless requests as "local" → full `/api/*` access
   without a token (as fallback user `sys_admin`).
2. **aetherCache.c stack overflow** (`strcpy`, VALUE_SIZE=256): `/api/edit_trade`
   value >256B overwrites the NEXT cache entry's key — spoof another user's trade.
3. Overwrite key to `user:1:trade:<uuid>` → poison the ADMIN's trade feed.
4. **HTML injection**: `/my_trades` renders `trade.data.action/price/symbol | safe`.
5. **CSP** (`script-src 'self' 'nonce-*' 'unsafe-eval'`) → XSS only via the site's
   own nonce'd `dashboard.js`:
   - DOM clobber `document.getElementById` (`<embed/name=getElementById>`) to force the try-block error
   - clobber `window.UI_DEV_MODE` (`<div/id=UI_DEV_MODE>`)
   - clobber `LOG_LEVEL` attrs (`<a/int="1/../../view/1"/id=LOG_LEVEL>`) to point
     the script's fetch at our data store `/front_end_error/view/1`
   - **prototype pollution** via the same-site read/write primitive
     `/front_end_error/new/1` with `{"__proto__":{"length":"<js>//"}}` → merged
     `logData.config.length` feeds `eval` → XSS executes.
6. **Exfil**: XSS posts `document.cookie` to `/front_end_error/new/exfil`
   (same-site primitive; CSP-safe) → solver reads it → admin session.
7. **RCE**: `upload_dataset` — `os.path.join(dir, file.filename)` with
   filename `../plugins/demo.tar` (regex allows `./`, endswith `.tar`,
   exiftool must see "file type: tar").
8. **Polyglot TAR/ELF**: build ELF via `as`+`ld` with a custom linker script
   (`.section .custom` = 10240 bytes of filler), build a TAR of dir `$'\x7FELF'`,
   then `dd` overlay tar bytes over the ELF at offset 120 → exiftool reads TAR,
   loader reads ELF.
9. `run_plugin` executes it (first `/bin/ls /` to find renamed
   `/flag<rand10>.txt`, then `/bin/cat` it) → flag.

## Reusable lessons

- **Hop-by-hop header stripping against reverse proxies** (Traefik ≤2.10.x,
  CVE-2024-45410): `Connection: <existing>, X-Real-Ip` — works whenever the app
  trusts proxy-added headers and has a "missing header = local request" fallback.
  Same shape as TornadoService's localhost gate — always ask "what header does
  the trust check use, and who strips it?"
- **Fixed-size strcpy in a custom daemon + app API exposing set() = controllable
  memory corruption** without any exploit code — overwrite ADJACENT LOGICAL DATA
  (the next cache entry's key).
- **DOM clobbering → prototype pollution → eval** is a full CSP-bypass kit when
  the app's own JS contains `eval` and merges untrusted JSON.
- A same-site store/fetch primitive (`front_end_error`) served as exfil channel,
  pollution source AND fetch target — primitive reuse compounds.
- Polyglot TAR/ELF via dd overlay at offset 120 beats content-scanners (exiftool).
- Timing: bot cycles on a 60s schedule — place poisoned state first, then poll
  the exfil endpoint; total ~2 min.

## Status of toolkit linkage

- This is the "long-chain" profile: writeup-first found the exact repo+solver.
  Blind-solving this ~20-solve chain without writeup is currently out of reach;
  the individual primitives are all captured in skills/ references.
