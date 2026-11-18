# Queue & Worker Sinks — async processing as the exec surface

## The shape — upload lands in a queue, a worker consumes it

```
upload → queued (kafka/sqs/rabbitmq/redis list/file-drop dir)
       → worker picks up → parses → processes → exec/impact
```

The upload response says `202`/queued — nothing executes yet. The
consumer is the real sink: a virus scanner, a transcoder, a parser, a
renderer, an ML worker, a CI runner.

## File-drop queue — the watch-folder sink

A dir the worker scans (`inotify`, polling, `incron`) — upload traverses
into it or lands there naturally:

- `.sh`/`Makefile`/`Rakefile` dropped in a build dir — the build execs it
- `.py`/`.js` dropped in a task dir — the runner executes it
- `inotify`-triggered processing → `chmod +x`-style execution or just
  parser reading

The watch dir is the hidden sink — find it via white-box source or
timing (upload → delayed processing evidence).

## Transcoder/converter workers — `ffmpeg`/`convert`/`gs`/libreoffice

A file-upload that goes through `ffmpeg`/`imagemagick`/`ghostscript`/
`libreoffice --convert-to` — the file IS parsed by that tool:

- ffmpeg on a crafted `.mp4`/`.m3u8`/`concat:` playlist — SSRF/file-read
  (`video-audio-attacks.md`)
- ghostscript on `.ps`/`.pdf` — `-dSAFER` bypass file-read/write
- libreoffice on `.docx`/`.pptx` — macro/DDE inside the conversion
- imagemagick `msl:`/`ephemeral:`/`label:`/`@` coder directives —
  `imagemagick-deep.md`

The transcoder IS the exec — upload content is the command.

## ML/model loading — `pickle`/torch/ONNX/keras

"Upload your model"/"load weights" features — `pickle.load`,
`torch.load`, `keras.models.load_model` — deserialization bugs —
`skills/web-deserialization/references/python-pickle-deep.md`. A `.pth`/`.pkl`/`.onnx`
upload reaching `torch.load` = pickle RCE.

## CI/build triggers — `Makefile`/`Dockerfile`/`.gitlab-ci.yml`

- file dropped into a build workspace → `make` runs it
- `Dockerfile` in a path the builder uses → image build execs it
- `.gitlab-ci.yml`/`.github/workflows/*.yml` — a repo write that lands a
  CI file — `post_exploitation`/`git-config` shapes

## The "the consumer is on a different host" boundary

The upload lands in a shared volume/bucket another service reads — a
microservice worker pod reading the bucket. The worker's lack of AV on
its input path is the gap — `authz-and-scope.md`'s cross-service.

## Detecting the queue — signals it's async, not sync

- `202 Accepted`/`queued`/`processing` status
- the uploaded file returns `"status":"pending"` then later changes
- a processing log/queue metrics endpoint
- delay between upload and file-availability
- a `X-Queue`/`X-Task-Id` header

The queue response tells you the file is going somewhere — find where.

## The "wait for the tick" strategy

After landing the payload, the consumer runs on its own schedule — poll
the output/result endpoint, or the OOB listener catches the callback.
`oob_listener.py` captures the out-of-band signal for blind sinks.

## Falsifiers

- no consumer reads uploaded files (upload stores and serves, nothing
  else)
- the consumer is sandboxed/stripped AND its parse rejects all payloads

## Output to record

- which worker reads uploads + its trigger cadence + the file-type it
  accepts
