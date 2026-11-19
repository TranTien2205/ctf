# Mechanism index — the primitive catalogue, indexed

## The two entry points

- **Local driver** — a `chromedriver`/`geckodriver` you run -> debugging aid.
- **Exposed endpoint** — a driver/Grid/CDP the challenge runs -> attack surface.

Both use the same command set; the difference is whose browser it is.

## The command primitives

| Primitive | Command | Read-back |
|---|---|---|
| create | `POST /session` | `sessionId` |
| navigate | `POST .../url` | via source/screenshot |
| read DOM | `GET .../source` | rendered text |
| run JS | `POST .../execute/sync` `/async` | return value |
| read jar | `GET .../cookies` | cookie list |
| capture | `GET .../screenshot` | PNG |
| destroy | `DELETE .../session` | — |

## The reach primitives

| Reach | Through | Holds |
|---|---|---|
| file | `file://` nav or `fetch` | source, flag, keys |
| loopback | `localhost` nav | internal routes |
| origin | `execute` `fetch` | same-origin APIs, flag page |
| jar | `GET /cookies` | HttpOnly flag cookie |
| storage | `execute` `localStorage` | token, flag |
| render | `screenshot` | image-carried flag |

## The observability primitives (local bot)

| Channel | Hook |
|---|---|
| console | `page.on("console")` |
| page errors | `page.on("pageerror")` |
| DOM | `page.content()` |
| network | `page.on("request"/"response")` |
| deeper | CDP `Network.*`, `Runtime.*` |

## The capability vs debugging split

```
whose driver? --mine--> debugging aid -> observability primitives
            \--theirs-> attack surface -> reach primitives
```

## Index to depth

| Need | File |
|---|---|
| the API | `webdriver-api.md` |
| the primitives | `per-mechanism.md` |
| the reach | `per-surface.md` |
| the reads | `per-vector.md` |
| the gates | `per-check.md` |
| the kills | `per-falsifier.md` |
| CDP depth | `cdp.md` |
| Grid | `grid-remote.md` |
