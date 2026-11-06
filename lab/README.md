# lab/vulnapp.py — the offline evaluation target

Deliberately vulnerable single-file app, **stdlib only** (no pip needed,
Windows-friendly). One planted bug per Argus probe family:

| Route | Planted issue |
|---|---|
| `/search?q=` | reflected XSS (no escaping) |
| `/item?id=` | SQLi — error-based + boolean-blind (sqlite) |
| `POST /login` | SQLi auth bypass (`' OR '1'='1`) |
| `/ping?host=` | command injection (sleep separators) |
| `/hello?name=` | SSTI (`{{7*7}}` → 49) |
| `/download?file=` | path traversal (`../`, `/etc/passwd` via fakefs) |
| `/redirect?next=` | open redirect |
| `/api/user/<id>` | IDOR — any id served |
| `/api/data` | CORS: reflects any Origin + credentials |
| `/token`, `/api/me` | JWT HS256, weak secret `secret123` |
| `/.git/HEAD`, `/debug`, `robots.txt` | info disclosure |

```bash
python lab/vulnapp.py 8777
python -m argus run http://127.0.0.1:8777
```

Do NOT expose this app beyond localhost — it is vulnerable on purpose.
