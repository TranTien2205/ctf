# Field notes — Unrestricted file upload

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

## 2026-09-19 · Magicom · proposed

- source note: `solved/htb-magicom-argv-injection-phar-jpeg-config-cmdi.md`
- chain card: `knowledge/chains/htb-magicom-argv-injection-phar-jpeg-config-cmdi.json`
- verification: verified_live — The flag was printed into the body of a live HTTP response from /cli/cli.php on the supplied instance, after the uploaded phar-JPEG supplied a config whose database value injected the setuid /readflag binary. The same request was repeated with plain curl and the flag appeared under the HTTP/1.1 200 OK and X-Powered-By: PHP/8.1.28 headers.
- classified as: `web-file-upload` (score 3.5, 3 signals matched)
- also matched: `web-deserialization` (3.0), `web-request-smuggling` (2.5), `web-ssrf` (2.5)
- signals that fired: import, magic byte, multipart/form-data

**Confirming probe that worked**

> GET the CLI-only script twice: once normally, and once with an argv-shaped query string containing no '=' sign, for example /cli/cli.php?+-m+healthcheck (pick whatever harmless mode the script defines).

Expected: The plain request answers with the command-line refusal message; the argv-shaped one does not, and instead produces the script's own output or a different error. That proves register_argc_argv is On and every argument of the script is attacker-controlled.

Falsifier: Both requests return the same refusal message. Then register_argc_argv is Off or the gate checks php_sapi_name(), the whole chain is closed, and the next mechanism layer should be tried instead of more query-string spellings.

**Traps recorded on this solve**

- When the payload is written into a structured data file, the format's own metacharacters break it silently. Here the command sits in an XML attribute, so a literal double quote, '<' or '&' makes DOMDocument fail, the config comes back empty and the response is a blank 200 that looks like the exploit regressed. '2>&1' is the usual casualty - use 2>/dev/null, or 2>/tmp/e followed by cat.
- A published solver's credentials may be decoys. Here root/rootganteng was invalid on the target and it made no difference, because the command it belongs to is meant to fail before the ';'.
- The mysql client in these containers often has no unix socket - pass -h 127.0.0.1 or it exits non-zero with no output.
- Do not chase execution of the uploaded file itself. It is renamed to random hex with a forced extension and served as an image; it is read as data through phar://, never run.
- A few magic bytes are not a valid image. Build real images with a library before drawing conclusions about which formats an upload filter accepts.
- phar.readonly=On on the target does not block this chain. It restricts creating archives, not reading them, and the archive is built on the attacker's own machine.
- Every run of the exploit uploads again. Batch commands into a single payload instead of running the chain once per command.

**Blast radius**: The final step is arbitrary command execution as the web user on a shared instance, so every command must be chosen deliberately: prefer id, ls, cat and the challenge's own setuid flag reader, and never a command that writes outside a directory you created. The upload step adds a real row to the application's database and a real file to its upload directory on every single run, and the exploit needs one upload per command, so an interactive session litters the instance quickly - batch several commands into one payload with ';' rather than running the chain repeatedly. Cleaning up afterwards may be impossible: the application's database account here held SELECT, INSERT and UPDATE but no DELETE, so the uploaded files could be removed but the rows could not. Assume that before starting and keep the number of uploads small.

- status: proposed

## 2026-09-23 · Resizer · proposed

- source note: `solved/htb-resizer-filename-traversal-olefile-so-import.md`
- chain card: `knowledge/chains/htb-resizer-filename-traversal-olefile-so-import.json`
- verification: verified_live — A single POST of a text file named zq1.txt returned HTTP 200 whose body was the flag, copied there moments earlier by the ELF constructor during the same request's failed image open. After the cleanup restart the same request no longer returns a flag and the site still answers 200.
- classified as: `web-file-upload` (score 3.5, 3 signals matched)
- also matched: `web-ssti` (3.5), `web-race-condition` (1.5), `web-prototype-pollution` (1.5)
- signals that fired: import, os.path.join(app.config['UPLOAD_FOLDER'], file, upload

**Confirming probe that worked**

> Upload the same filename twice, then upload it once more in a path-equivalent form such as ./name or dir/../name.

Expected: The second and third uploads are both rejected as duplicates, showing the raw filename reaches os.path.join and the check resolves paths.

Falsifier: The equivalent forms are accepted or the name is rewritten, meaning the filename is sanitised and there is no traversal to build on.

**Traps recorded on this solve**

- The duplicate-file message is an existence oracle that WRITES on a miss. Probing a path creates it, which can overwrite the exploit's own payload; use throwaway names.
- The duplicate check short-circuits before the file is saved and before the library runs, so re-uploading an existing name never triggers anything. Retries need fresh names.
- Lazy plugin initialisation happens once per worker process. Workers that already met an unidentifiable file before the payload was planted will never import it again; a fresh worker is required.
- Compile the payload's destinations in plural. A single destination whose read slot was already consumed during testing leaves the secret copied somewhere unreadable.
- Sizing a decode just under the library's decompression-bomb ceiling avoids the guard and still exhausts the worker, which restarts the container and wipes the application directory. That is both the only delete primitive and a destructive act.
- Do not conclude the processing library from the absence of a feature alone; confirm it. Dropped text chunks and a single IDAT in the output identified Pillow and ruled out the ImageMagick profile-read CVE.

**Blast radius**: The planted shared object executes as the application user on any later request that triggers the lazy import, so it is a backdoor for every other visitor until removed. The payload's copies of the secret sit in a directory other users of the instance may be able to reach. Forcing the restart that clears them kills in-flight requests and wipes everything else written to the application directory, including other people's uploads. Concurrent oversized decodes are what force that restart; keep them to one burst and only on an instance you own.

- status: proposed
