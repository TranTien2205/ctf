# Field notes — OS command injection

Written by `tools/classify_solve.py` after a flag is verified, then reviewed by a
human. Nothing here is generated from guesswork: every entry cites the solved note
and the chain card it came from.

| Status | Meaning |
|---|---|
| `proposed` | written automatically after a solve; not yet reviewed |
| `confirmed` | a human checked it against the evidence and kept it |

Promote an entry by changing its status line to `confirmed`. Delete an entry that
did not hold up, and say why in the commit message. `test/regression.py` fails if
an entry has any other status.

---

## 2026-09-27 · pcalc · confirmed

- source note: `challenges/pcalc/state.json`
- chain card: `knowledge/chains/htb-pcalc-php-eval-letter-filter-highbyte-constant-tilde-complement-rce.json`
- verification: verified_live — Live HTB instance. The character sweep returned the filter message for exactly the 54 characters [a-zA-Z"'] and nothing else. GET /?formula=_ rendered _ . GET /?formula=~(%8C%86%8C%8B%9A%92) rendered system. GET /?formula=(~(%8C%86%8C%8B%9A%92))(~(%96%9B)) rendered uid=1000(www) gid=1000(www) groups=1000(www). ls / showed a randomised flagYrsQz at the root and cat of it returned the flag. Recorded in challenges/pcalc/state.json through tools/hooks.py post-probe (confirms, evidence-kind impact) and pre-flag (source live-response). Afterwards the application source was read through the same primitive and confirms every inference: models/CalcModel.php rejects on strlen($formula) >= 100 || preg_match_all('/[a-z\'"]+/i', $formula), then runs eval('$pcalc = ' . $formula . ';') and catches ParseError; php -v reports PHP 7.4.33.
- classified as: `web-command-injection` (score 1.83, 2 signals matched)
- also matched: `web-nosqli` (1.07), `web-parser-differential` (1.04), `web-request-smuggling` (1.0)
- signals that fired: command-injection, uid=1000(

**Confirming probe that worked**

> GET /?formula=_   (a single underscore, nothing else)

Expected: the page renders _ . An undefined constant became its own name, so the runtime is PHP 7.x and the high-byte constant trick is available

Falsifier: it renders an error or nothing. On PHP 8 an undefined constant is an Error, so this route is closed and the chain falls back to the slower INF/NAN plus XOR construction in step 3

**Traps recorded on this solve**

- the two rejection messages mean opposite things and look equally final. 'dont bite the hand that feeds you human' is the filter; 'report to the nearest galactic federation agency' is a caught ParseError, which means the character got through. Thirty characters that appear blocked in a naive sweep are actually accepted.
- the filter message is ALSO returned for an over-long payload, because the length check and the character check share one branch. A correct technique therefore reads as a filtered one as soon as the payload grows; measure the cap on its own before concluding a character is forbidden. The first working construction here was 170 bytes and was misread as a filter hit.
- a falsy result renders no alert at all, so an empty page is 0, false or the empty string, not a failure. Do not treat a blank answer as a dead probe.
- eval is an ASSIGNMENT here, eval('$pcalc = ' . $formula . ';'), not a return. Anything after a ; is evaluated but discarded, which is why 1;2 answers 1 -- useful to know before building a multi-statement payload that appears to be ignored.
- (0/0)[1] answers nothing: a float cannot be offset. Concatenate first, and concatenate with a PARENTHESISED digit -- (0/0).1 is a parse error because .1 lexes as the float 0.1, while (0/0).(1) is the string NAN1.
- system() prints its output directly and RETURNS only the last line, and it is the return value that lands in the template. Pipe multi-line output through tr, or use a command whose last line is what you want.
- the high-byte constant route is PHP 7 only. PHP 8.0 turns an undefined constant into an Error, so the same payload dies there and the fallback is the much longer INF/NAN plus XOR construction.

**Blast radius**: This ends in command execution as the web user, so treat every command as a write. Keep them read-only (id, ls, cat) and never redirect output into the document root on a shared instance. Nothing was written to the target in this solve. The 99-byte cap is an accidental safety rail: it is too small for most destructive one-liners, which is a reason not to work around it by dropping a file.

- status: confirmed
