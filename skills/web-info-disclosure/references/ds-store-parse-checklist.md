# .DS_Store parsing — checklist

macOS directory metadata: a binary file listing the directory's real contents — filenames, including ones never linked.

## Checklist

- [ ] Fetch /.DS_Store (and per-dir: /uploads/.DS_Store etc.).
- [ ] Parse with a .DS_Store parser or strings + structure knowledge — the file list is the prize.
- [ ] Each filename found is a targeted probe.
- [ ] Recurse: a .DS_Store in a found dir lists that dir's contents.

## Abort conditions

- It's binary — strings gives partial names; a real parser gives the full list.
- Hidden files appear in .DS_Store even though directory listing is off.
- Per-directory: probe .DS_Store inside every discovered directory.

## Falsifier

Falsifier — no .DS_Store on any dir: the channel is closed (Windows boxes use Thumbs.db instead).
