# Embedded-Payload Chains — the file that carries the attack inside

## The pattern — the file's FORMAT carries a different attack class

The upload is a valid document/image/archive — but inside it, a
feature/field/stream IS a payload for another bug class:

| File | Embedded payload | The real bug |
|---|---|---|
| `.docx` | `w:object`/`oleObject` OLE | activeX/OLE exec |
| `.docx` | `settings.xml` `w:attachedTemplate` | remote template = xxe/ssrf |
| `.docx` | `word/_rels` `.rels` `Target=file:///...` | external rel = file-read |
| `.xlsx` | `externalLinks/` part | external link = ssrf/file-read |
| `.xlsx` | `DDE`/`cmd` formula | csv-dde-injection |
| `.svg` | `<script>`/`onload`/`foreignObject` | xss |
| `.svg` | `<image href="file:///..."/>` | ssrf/file-read on render |
| `.svg` | `xlink:href`/`use` external | ssrf |
| `.pdf` | `/JS`/`/JavaScript`/`/OpenAction` | pdf-js exec |
| `.pdf` | `/Launch`/`/EmbeddedFiles` | exe/pdf launch |
| `.pdf` | `/URI`/`/GoTo` remote | ssrf |
| `.epub` | `.opf`/`xhtml` xxe/script | epub is zip of xhtml = xss+xxe |
| `.mp4`/`.m3u8` | `EXT-X-KEY`/`file://`/`concat:` | ffmpeg file-read (`video-audio`) |
| `.png`/`.jpg` | `iTXt`/`zTXt`/EXIF metadata | xxe-in-exif or sql/cmd-in-meta |
| `.wav` | metadata/`LIST INFO` | meta-injection |
| `.ttf`/`.otf` | name table | embedded strings |
| `.woff` | XML metadata | xxe |
| `.ps` | ghostscript ops | gs file-read/-dSAFER bypass |
| `.eps` | same gs | same |
| `.ico` | embedded png/bmp | nested-parse |
| `.lnk` | windows shortcut | icon-path/ssrf on render |
| `.desktop` | exec= | exec-on-open |
| `.htaccess` | `php_value`/`AddHandler` | handler-override (`init-hooks`) |
| `.user.ini` | `auto_prepend_file` | prepend-exec (`init-hooks`) |
| `web.config` | handler map | iis handler (`iis-deep`) |
| `.vimrc`/`.emacs` | modeline | editor-exec |
| `.bashrc` | command | shell-init (`init-hooks`) |
| `Makefile`/`Rakefile` | recipe | build-exec |
| `Dockerfile` | RUN | build-time exec |
| `.gitlab-ci.yml`/`.github/workflows` | run: | ci-pipeline exec |
| `composer.json`/`package.json` | scripts | install-time hooks |
| `.sql` | statements | import-exec (`backup-restore`) |
| `config.php`/`settings.py` | code | config-as-code |
| `.toml`/`.yaml` config | parsed | yaml-deser/ssti |
| `.pth` | `import ...` | python-startup (`python-specific`) |
| `.py`/`__init__.py` | code | python-module shadowing |

## The "the upload is the trojan horse" rule

The parser's check reads the OUTER format (a valid docx/svg/zip); the
sink reads an INNER structure (an entity, an OLE object, a rel target).
Finding the inner feature is the whole game — `polyglot-files.md` for
the format-level variant, this file for the feature-level one.

## The discovery method — enumerate the format's part tree

- docx/xlsx/epub — unzip the file, list parts, find each `Target`/`href`/
  `src`/`embed` reference — any part referencing external content is a
  potential ssrf/file-read
- pdf — `/URI`, `/JS`, `/OpenAction`, `/Launch`, `/EmbeddedFiles`,
  `/Names` — each action dict is a hook
- svg — `<image>`, `<use>`, `<script>`, `xlink:href`, `foreignObject`
- font — name-table/metadata strings
- media — metadata tags, cue tracks, codec parameters
- archive — `zipslip`/`tarslip`/`LNKTYPE`/`FNAME`

## The "the embed survives a re-encode" test

- image `iTXt`/`zTXt` text chunks get stripped on re-encode — the payload
  dies unless the parser reads them BEFORE re-encode
- docx `custom.xml`/`settings.xml` parts survive a "rezip" if the app
  just re-saves it
- pdf `/JS` survives a read-not-rerender path

## The "consumer reads a DIFFERENT field" trap

- a `.png` whose EXIF metadata carries `<?php` — the image serve doesn't
  run it; a metadata-viewer/`exif_read_data` consumer does
- a `.docx`'s `docProps/core.xml` title field — parsed and shown in a
  document-info view — a field-level injection via the docx part

## The "chained carriers" — polyglot × embed

- a `GIF89a` polyglot whose inner text chunk is `<?php` — passes
  magic+parse, execs via include
- a zip containing a docx containing an OLE — the zip is the upload
  vehicle, the docx is the payload, the OLE is the exec

## Falsifiers

- the consumer strips/skips the embedded feature's fields
- the format's features don't reach a sink that executes/reads them

## Output to record

- the embedded feature + its carrier part + the sink it reaches
