# Attack shapes deep — the named patterns, staged out

## Shape 1: the local reproduction (the default)

```
read bot source -> extract URL/cookie/wait/flags/version
-> local driver, same -> set cookie, navigate, wait
-> four hooks on -> canary -> iterate -> confirm
-> check exfil channel -> fire live once
```

The most common shape — a debug loop replacing blind visits. The
reproduction's fidelity is the whole game; every later step depends
on it matching live.

## Shape 2: the exposed-endpoint file read

```
POST /session -> sessionId
-> nav file:///flag -> GET /source -> flag text in <pre>
-> or nav file:///proc/self/environ -> source -> FLAG=...
-> pre-flag -> DELETE
```

The direct capability. The `/proc/self/environ` fallback is the high-
yield read when `/flag` guesses miss — env vars carry the path.

## Shape 3: the JS-read pivot

```
POST /session -> sessionId
-> execute/sync fetch("file:///flag") -> the file text
-> or execute document.cookie / localStorage / fetch("/api/flag")
-> pre-flag -> DELETE
```

When `file://` navigation is blocked but `execute` runs — the JS file
read is a separate primitive from the navigation read.

## Shape 4: the loopback pivot

```
POST /session -> sessionId
-> nav localhost/admin -> GET /source -> internal admin
-> execute fetch(localhost/api/flag) -> flag
-> pre-flag -> DELETE
```

The browser's host position reaches routes the external view cannot.

## Shape 5: the jar read

```
POST /session -> sessionId
-> GET /cookies -> the jar incl. HttpOnly -> flag cookie
-> pre-flag -> DELETE
```

The HttpOnly flag cookie — the jar reads what `document.cookie` cannot.

## Shape 6: the same-origin write-back

```
stored payload in bot's browser
-> payload writes flag to a same-origin store (profile/note/comment)
-> you fetch the store -> flag
-> pre-flag
```

Egress blocked — the flag never leaves; the app itself is the channel.

## Shape 7: the rendered read

```
POST /session -> sessionId
-> nav the flag page -> GET /screenshot -> decode PNG -> flag
-> pre-flag -> DELETE
```

The flag rendered as an image — the PNG is the artifact.

## Shape 8: the multi-stage chain

```
XSS developed locally (shape 1)
-> fires in live bot -> exfils credential/token
-> replay the cred -> reach the next class (template write, RCE)
-> the follow-on class's flag -> pre-flag
```

The real CTF shape — the browser is the connector between the
injection class and the follow-on class. Each stage confirmed locally
before the live fire.

## The selection tree

```
endpoint answers? --yes-->
  file read works?        -> shape 2
  execute works?          -> shape 3 (or jar 5)
  localhost reachable?    -> shape 4
  flag is a cookie?       -> shape 5
  flag rendered?          -> shape 7
\--no-->
  bot flow + payload? -> shape 1 -> shape 8 (chain) or shape 6 (egress)
```
