# Detection Contexts — where command injection actually hides

## The obvious surface — utility endpoints

```
/ping /traceroute /trcrt /nslookup /dig /host /whois /arp /nmap
/health-check /network-test /diagnostics /tools/ping
```

Params: `host`, `ip`, `addr`, `domain`, `target`, `server`, `node`.

These are the canonical cmdi surfaces — a name that IS a command usually
means a command is run. `ctf-shapes.md` has the full catalogue.

## The hidden surface — tools the app wraps

| Endpoint hint | Underlying command | Injectable param |
|---|---|---|
| `/convert`, `/resize`, `/thumbnail` | `convert`/`magick`/`ffmpeg` | filename, size, format args |
| `/pdf`, `/report` | `wkhtmltopdf`, `gs`, `pandoc` | url, filename, template |
| `/export`, `/backup`, `/archive` | `tar`, `zip`, `rsync`, `mysqldump` | path, filename, tables |
| `/git`, `/clone`, `/repo` | `git clone`/`git fetch` | url, branch, dir |
| `/search`, `/grep`, `/find` | `grep`, `find`, `locate` | pattern, path |
| `/check`, `/verify`, `/lint` | `php -l`, `node --check`, `shellcheck` | filename |
| `/compress`, `/optimize` | `optipng`, `jpegoptim`, `pngcrush` | filename, flags |
| `/scan`, `/av` | `clamscan`, `yara` | path |
| `/cert`, `/tls` | `openssl` | hostname, cn, config |
| `/send`, `/mail` | `sendmail`, `mail`, `msmtp` | to, subject |
| `/cron`, `/schedule` | `crontab`, `at` | any field |
| `/restart`, `/service` | `systemctl`, `service`, `supervisorctl` | service name |
| `/logs`, `/log` | `tail`, `grep`, `journalctl` | file, lines, pattern |
| `/ssh`, `/remote` | `ssh`, `scp`, `rsync` | host, user, args |
| `/dns`, `/resolve` | `dig`, `nslookup`, `host` | name, type |
| `/download`, `/fetch`, `/import` | `curl`, `wget`, `aria2c` | url, -o path, flags |

## Parameter shapes that suggest command use

- value looks like a hostname/IP/filename → probably a command arg
- param named like the flag: `host`, `target`, `-c`-like names
- value joins a documented command: page says "runs ping -c4 HOST"
- response contains raw command output (PING headers, dig SOA blocks,
  traceroute hops)

## Non-obvious surfaces — data reaching shell indirectly

| Carrier | How input reaches shell |
|---|---|
| filename in upload | `mv "tmp" "$uploads/$filename"` — `;` in filename → `filename-injection.md` |
| uploaded file's content | app runs `grep $pattern file`, file name flows into command |
| EXIF/metadata fields | `identify -format "%[exif:$field]"` — field value into cmd |
| DB field → CLI | stored username used in `mail $user` cron — `second-order.md` |
| log lines | app greps/`tail`s logs containing your UA string |
| JSON field | `{"host":"x;id"}` decoded then shelled |
| HTTP header | UA/Referer/XFF reaching a log-processing shell |
| cookie value | session cookie decoded then used in a command |
| template/config field | hostname config written to a shell script that runs |
| archive entry name | zip entry `../;id` reaching `unzip` or post-process |
| PDF/image content | `convert "$f" x.png` — the FILENAME field, not content |

## The reflected-command response — the app echoes the command it ran

Some apps echo `running: ping -c4 127.0.0.1` — free template disclosure:
you now know the quoting, position, and tail text. Treat it as white-box.

## Timing-based discovery — when there's no output

The endpoint may inject into a command whose output isn't shown — only
timing reveals it:

- `;sleep 5` vs baseline — repeatable 5s = confirmed shell
- `$(sleep 5)` — inside quotes
- `|sleep 5` — pipe variant
- `--` arg-style: `sleep` can't be an arg → needs separator

For Windows: `& timeout /t 5` / `& ping -n 5 127.0.0.1`.

## The "looks like cmdi but isn't" traps

- SSTI: `{{7*7}}` works → `web-ssti`, not cmdi — but `<%= system %>`-style
  templating can reach exec → the boundary is which evaluator runs it
- PHP code injection `eval($_GET)` — `eval-injection.md` (same class per
  chain card)
- SQLi stacked queries calling `xp_cmdshell`/`INTO OUTFILE` — `web-sqli`
- expression language injection (SpEL/OGNL/MVEL) — `eval-injection.md`
- XPath/regex evaluators — different class, don't route here

## The args-vs-shell call boundary — how to tell from output alone

`ping x;id` →
- shell boundary: `uid=33(www)` appears
- argv boundary: `ping: x;id: Name or service not known` — the `;` is
  INSIDE the hostname error = argv element, no shell. **Falsifier.**

## Output to record

- the endpoint + param + the template shape if the app echoes it
- the channel that proved the boundary (output/error/time)
