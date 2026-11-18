# Log Poisoning → Command Injection — the log that gets shelled

## The shape — your bytes land in a log; a shell later reads them

```
request → access/error log → admin tool / log-analyzer / grep / fail2ban
                          → a shell command runs over log lines
```

`LogPoisoning` has two faces: (a) log file contents reach a shell or
an include (`php://`/`file=` LFI includes access.log → `<?php` in UA
executes), (b) a field inside the log is `system()`'d/`exec()`'d by a
log-processing tool.

## Carrier fields — what lands in the log

| Log source | Attacker-controlled bytes |
|---|---|
| `access.log`/`error.log` | URL path, query, UA, Referer, cookie name |
| app log | username, error message, trace fields |
| auth log (`/var/log/auth.log`) | username field — `Failed password for X` |
| mail log | From/To fields |
| fail2ban/fail2web logs | the banned-IP field |

## The include path — the `<?php` in UA classic

```
UA: <?php system($_GET['c']);?>
GET /vuln.php?file=/var/log/apache2/access.log → php executes the UA bytes
```

This is `web-file-upload`/`file-read-primitives` territory for the LFI
side — the cmdi-skill angle is the LATER shell over the log.

## The shell-over-logs side — `grep`-style processing

A log analyzer does `cat access.log | grep $pattern | awk '{print $1}'` —
the `$pattern` is your search input — classic cmdi into the SEARCH
command. Or `awk`/`sed` on a line containing your bytes → the awk/sed
script reaches `system()`/`e`-command — `argument-injection.md`'s awk
`BEGIN{system()}` and sed `e` exec.

## `fail2ban`/`denyhosts`-style — a log-parsed action

`actionban = iptables -I INPUT -s <ip> -j DROP` — the `<ip>` comes from
the log line — a spoofable field reaching iptables. `Whois`-hook or
`action` commands take the field — classic second-order.

## Detection — find the consumer

- does any admin/report/tool endpoint read logs? (`/admin/logs`,
  `/logs`, `/view-log`, `/audit`)
- does a tool `tail`/`grep`/`awk`/`journalctl` logs with your field
  inside?
- does a scheduled job (`cron`/`timer`) parse logs?
- is `fail2ban`/`denyhosts`/`ossec` running?

## The payload form — bytes that survive logging AND exec

- logging munges control chars sometimes — `%0a` may be logged raw or
  decoded depending on logger
- the payload needs to survive the log's charset/escaping AND match
  the shell's grammar when extracted
- `';id;'` inside a URL path — Apache logs the raw path —
  `GET /x';id;'` → log contains `x';id;` — if a shell parses the log
  line field at that position → exec

## Falsifiers

- no tool/process reads the log within reach of a shell
- the logged bytes are escaped/sanitized before any command use
- the log path isn't reachable by any include primitive (for the LFI
  variant)

## Output to record

- the log file + the consumer command + the verbatim log line carrying
  the payload
