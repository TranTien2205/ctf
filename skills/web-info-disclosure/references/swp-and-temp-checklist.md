# Editor swap and temp files — checklist

Vim .swp, Emacs #file#, nano .save, Windows ~$: the editor's crash-recovery copy of a source file, served as text.

## Checklist

- [ ] Probe .<file>.swp, <file>~, <file>.bak, <file>.old, <file>.save for each known filename.
- [ ] swp files are vim binary — strings or vim -r recovers the edited text.
- [ ] A .swp may be an OLDER version than the live file — diff against the served code.
- [ ] Temp files for CONFIG files (.env.swp) are the highest-value targets.

## Abort conditions

- The swap file's name pattern is .<name>.swp in the same directory.
- Multiple .swo/.swn files exist for crashed multi-session edits.
- A stale .swp may hold a flag-bearing version since overwritten.

## Falsifier

Falsifier — no swap/temp file for any known filename: no editor leftovers.
