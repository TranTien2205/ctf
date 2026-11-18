# Read Pipeline — the ordered escalation ladder

## The rung-order — cheapest signal first

```
Rung 0: absolute-path /etc/passwd          — reaches-fs?
Rung 1: traversal depth 1..8               — syntax right?
Rung 2: null-byte / terminator             — extension-append?
Rung 3: encoding (URL/double/UTF-8-exotic) — byte-filter?
Rung 4: php://filter base64               — binary-safe read?
Rung 5: phar:// / zip:// / glob://        — wrapper reach?
Rung 6: expect://                         — exec?
Rung 7: file://dir/ (Java dir-list)       — listing?
Rung 8: /proc/self/* — the self-view
Rung 9: include-as-exec — the RCE sink
```

## The per-rung falsifier — when to move on

- Rung 0 empty → try Rung 1; if all fail → the class may be dead
- Rung 0 errors naming the path → the read TRIED → the file just
  doesn't exist → try a known file
- Rung 0 echoes literal → no parse → the param isn't reaching fs
- Rung 4 b64 that doesn't decode → the wrapper isn't reaching
- Rung 9 `include` that doesn't exec → it's a read-sink

## The "the primitive narrows the corpus" — what to read

- the read works → `/proc/self/cmdline`+`cwd`+`environ` → the app path
- the app path → the source → the flag-path
- the flag-path → the flag → `pre-flag`

## The "the read-loop" — `read_loop.py`

```bash
python3 tools/web/read_loop.py --url http://target/page \
  --method GET --body 'file={path}' \
  --profile container --extract-paths
```

`read_loop` walks a wordlist of paths, baseline-classifies each —
`--profile container` leads with `/proc/self/mountinfo`.

## The "the read-loop is bounded" — the wordlist cap

`read_loop` walks a LIST — the list is bounded — the path-order is
the read-priority — `flag-paths.md`/`source-location.md`/`linux-paths.md`/
`windows-paths.md` are the list-sources.

## The "the response-shape" — raw vs structured

- raw file content — `root:x:0:0:` — the read is inline
- inside a JSON `{"data": "..."}` — parse the field
- inside a template `The file is: ...` — extract the middle
- inside a download `Content-Disposition` — the file is the body

## The "the prefix/suffix-strip" — the echo-cleanup

The app may wrap the file in a template — `curl ... | cut -c115-` —
strip the prefix/suffix — the content is the middle.

## The "the read is confirmed, now chain" — the pivot

Once the read is proven:
1. `/proc/self/environ` → `FLAG` env?
2. `/proc/self/cmdline` → the app path
3. the app source → the flag-path
4. the flag-path → the flag → `pre-flag`

## The "the read fails at every rung" — the kill-map

`verdict=refutes` — the class is dead on this surface — record which
rungs died (the filter that blocked, the confine that held) — the
kill-map for the next attempt.
