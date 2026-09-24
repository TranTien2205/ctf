# Notebook Converter Pro — chain verified locally (remote flag NOT obtained)

- Web challenge. Flask notebook-to-HTML/Markdown converter running nbconvert 7.17.0.
- Remote target `154.57.164.73:30136` was down (connection refused) when this run
  happened, so the remote flag was not read.
- The full chain was reproduced end-to-end on a **locally built instance of the
  supplied source**. The only flag available there is the source test flag
  `HTB{REDACTED}` in `flag.txt`, which the Dockerfile moves to `/root/flag.txt`.
  That is a test value, not the challenge flag.
- Assistance: partially writeup-shaped. The file-read primitive was found by the
  system; the nbconvert `FilesWriter` path-traversal write and the `readflag`
  setuid target were derived from the supplied source.

## Stack

- Flask 3.1.0, gunicorn, nbconvert 7.17.0, nbformat 5.9.0.
- SQLite at `/srv/app/data/app.db`; the admin password is stored **in plaintext**.
- The app runs as `appuser` with `JUPYTER_CONFIG_DIR=/home/appuser/.jupyter` and
  `HOME=/home/appuser`.
- A conversion spawns `python /srv/app/app/converter/convert_job.py` as `appuser`.
- `/readflag` is setuid root and prints `/root/flag.txt`.

## Chain

1. Register and log in as an ordinary user.
2. **Arbitrary file read as appuser.** Upload a notebook whose markdown cell is
   `![f](/srv/app/data/app.db)` with `format=html`. `HTMLExporter.embed_images =
   True` inlines the referenced local path as a base64 data URI in the returned
   HTML. Download the job output and base64-decode the `<img alt="f" ...>` data.
3. Recover the admin password from the SQLite `users` table (plaintext).
4. Log out, log in as `admin`, then `POST /admin` with
   `asset_storage_enabled=on`. Only an admin can flip this.
5. **Arbitrary file write as appuser.** With asset storage on, markdown
   conversions use `FilesWriter`. In nbconvert 7.17.0,
   `ExtractAttachmentsPreprocessor` puts the markdown attachment key into
   `resources["outputs"]` and `FilesWriter._write_items` writes
   `os.path.join(build_dir, filename)`. The attachment key is not sanitized, and
   an absolute key resets the join, so the writer creates any absolute path:

   ```json
   {"cell_type": "markdown", "source": ["x"],
    "attachments": {"/srv/app/app/converter/convert_job.py":
                    {"text/plain": "<base64 of a Python payload>"}}}
   ```

   (The `outputs` path via `out.metadata["filename"]` also traverses, but it
   forces a mime extension; the attachments path does not.)
6. **RCE as appuser.** The next conversion runs the overwritten
   `convert_job.py`. The payload runs `/readflag` and writes its output into the
   job's exports directory, then prints valid JSON so the job is marked
   completed.
7. Download the job output to read the flag.

## Payload used for the overwritten converter

```python
import argparse, json, os, subprocess
p = argparse.ArgumentParser()
p.add_argument("--input"); p.add_argument("--output-dir")
p.add_argument("--format"); p.add_argument("--storage-mode")
a = p.parse_args()
out = subprocess.run(["/readflag"], capture_output=True, text=True)
data = (out.stdout or "") + (out.stderr or "")
path = os.path.join(a.output_dir, "flag.txt")
open(path, "w").write(data.strip())
print(json.dumps({"status": "ok", "output_path": path}))
```

## Local verification

```
[*] admin password: <recovered from app.db>
[*] admin login -> /dashboard
[*] enable asset storage 200
[*] write job  <overwrites convert_job.py>
[*] trigger job
[*] download 200 text/plain
[+] output: HTB{REDACTED}   (source test flag)
```

The remote challenge was not solved: the instance was unreachable, and the only
flag read was the test flag shipped in the source bundle.

## Reusable

- `HTMLExporter.embed_images = True` turns a markdown image reference into an
  arbitrary local file read; the response carries the file base64-encoded.
- nbconvert 7.17.0 `ExtractAttachmentsPreprocessor` does not sanitize attachment
  names (the fix is in later releases), so a markdown attachment with an absolute
  path is an arbitrary file write through `FilesWriter`.
- A converter invoked as a subprocess from a fixed script path is a code-execution
  target: overwrite the script and trigger one more conversion.

## Traps

- The admin password is regenerated on every app start (`reset_runtime_state`),
  so a password from an earlier run is stale after a restart.
- `public.login` redirects an already-authenticated session to `/dashboard`
  before reading the form; log out first to switch users.
- The first `data:...;base64,` in the HTML is an nbconvert template icon, not the
  target file; match the specific `<img alt="f" ...>` tag.
- The `outputs` filename path forces a mime extension (`.png`/`.jpg`/`.svg`/`.pdf`),
  so it cannot write a `.py` file; use the attachments path.
- `jupyter_nbconvert_config.py` is **not** loaded by the nbconvert Python API
  (`Exporter` is a `LoggingConfigurable`, not an `Application`), so writing that
  config file is not the trigger here.

---

## Live verification — 2026-09-24 (second run, different instance)

The original write-up above was a **local-only reproduction**; the card carried
`verification: unverified` because the remote instance was unreachable at the time.
This run confirmed the whole chain against a live target (`154.57.164.82:31655`) and the
card is now `verified_live`.

Preconditions were re-checked against the supplied handout before reusing anything:
`nbconvert==7.17.0`, `exporter.embed_images = True`, the `FilesWriter` saved-assets
branch, `/readflag` setuid root, and `chown -R appuser /srv/app` (so the converter script
is writable by the service user). All still true.

Sequence, each step confirmed by its own observable:

1. Card's `first_confirming_probe` reproduced exactly: `![f](/etc/hostname)` converted to
   HTML returned the host name inside the `alt="f"` data URI. (Trap confirmed: the first
   data URI in the page is a template icon, so the alt tag must be matched.)
2. `/srv/app/data/app.db` read back as 32768 bytes and opened directly with `sqlite3` —
   admin password in plaintext. Trap confirmed: it is regenerated per start, so it has to
   be read fresh on every run.
3. Fresh `requests.Session` used for the admin login (trap: an already-authenticated
   session is redirected past the login form).
4. Attachment key `/srv/app/app/converter/convert_job.py` with an `image/png` base64 value —
   `os.path.join(build_dir, "/abs/path")` discards the prefix, so the absolute key writes
   wherever it points.
5. One further conversion executed the replacement and the job download **was** the
   setuid helper's stdout.

### Improvement over the original run: leave nothing broken

The card previously said overwriting the converter "disables the application's conversion
feature until the container is rebuilt". That is avoidable. The replacement script embedded
the original converter source as base64 and rewrote itself immediately after producing its
output, so the outage lasted exactly one job.

Verified afterwards, not assumed: a normal notebook converted to proper HTML again, and the
converter re-read through the same `embed_images` primitive was **byte-identical** to the
shipped source. The global saved-assets setting was also switched back off.

**Lesson:** when the only destructive step in a chain is a file overwrite and you already
hold the original bytes, make the payload restore itself — then prove it by reading the file
back through the read primitive you already have, rather than trusting that it worked.
