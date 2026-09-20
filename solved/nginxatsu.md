# nginxatsu — SOLVED (assisted: writeup)

- Platform: HackTheBox (web, original 2021 — NOT "baby nginxatsu")
- Date: 2026-09-06
- Flag: `HTB{REDACTED}` (HEX-verified against DB row)
- Artifacts: `~/ctf/challenges/nginxatsu/{exploit.py, exploit_threaded.py, exploit_fast.py}`
- Writeup used: d4rkstat1c Medium writeup + `d4rk007/ctfs/nginxatsu/nginxatsu.py`
  (found via websearch AFTER ~10 rounds of manual fuzzing — the waste; search earlier)

## Chain

1. Fingerprint: nginx + PHP 7.4 + Laravel error pages; app generates nginx configs.
2. nginx alias traversal leaks source: `/assets../.env` (APP_KEY + DB creds),
   `/assets../app/Http/Controllers/API/ConfigController.php`.
3. Controller: `orderBy(Session::get('order'), Session::get('direction'))` —
   session lives in an AES-CBC encrypted cookie (SESSION_DRIVER=cookie), so the
   leaked APP_KEY lets us forge the whole session.
4. Cookie format: `nginxatsu_session` = b64(JSON{iv,value,mac}); second cookie
   (name = session id) decrypts to JSON `{"data":"<php-serialized session>","expires":ts}`;
   session keys include `username`, `order`, `direction`.
5. Blind SQLi oracle on `GET /api/configs`: TRUE -> 200, FALSE -> 500, using
   `order` = `id->"')), (SELECT (CASE WHEN (COND) THEN 'SUCCESS' ELSE (select exp(~(SELECT * FROM (select user())x))) END)) #`
6. Exfil: table `definitely_not_a_flaaag` (LIKE '%fl%'), column `flag_8Wi6s`
   (LIKE '%flag%'), flag via ASCII binary search (~7 probes/char).
7. Verify: `(SELECT HEX(SUBSTRING(col,1,200)) ...) = '<flag hex>'` -> TRUE.

## Reusable lessons

- **Writeup-first for known platforms** (see playbook): manual nginx-config fuzzing
  produced nothing; the writeup located the whole chain in minutes.
- **CI-collation trap**: `'t' = 'T'` is TRUE under MySQL *_ci collations —
  case-exact extraction needs `= BINARY('c')`, and a string `.replace()` done
  AFTER `.format()` cannot match the `'{ch}'` placeholder (bug I hit twice).
- **Blind exfil speed**: linear charset scan ~90 probes/char timed out twice;
  ASCII binary search (~7 probes/char) finished in minutes. Default to binary search.
- Leaked APP_KEY + cookie session driver = full session forgery (Laravel pattern).
