# NextPath — SOLVED

- HackTheBox web challenge. Next.js career landing page.
- Flag read from a live response: `HTB{REDACTED}` (body of `/api/team`, read from `/flag.txt`).
- Assistance: writeup-assisted. The route and its filters were found independently; the duplicate-parameter array bypass and the 100-character truncation shaping were taken from a public writeup after the direct traversal was rejected.

## Stack

- Next.js (pages router), Node.js.
- `/api/team?id=<n>` reads `team/<n>.png` and returns it as `image/png`.
- The handler validates the id with `ID_REGEX = /^[0-9]+$/m`, then rejects `query.id.includes("/") || query.id.includes("..")`.
- The path is built with `path.join("team", query.id + ".png")` and read with `fs.readFileSync(filepath.slice(0, 100))`.

## Chain

1. Request `/api/team?id=1` and note the PNG response; request a missing id and read the `ENOENT ... open 'team/<id>.png'` error, which reveals the path construction.
2. A direct traversal (`id=../../../../flag.txt`) returns "Invalid format" or the traversal rejection.
3. Send duplicate `id` parameters so `query.id` becomes an array: `?id=1%0A&id=<traversal>`.
4. `ID_REGEX.test(array)` coerces the array to a comma-joined string whose first line is numeric, so the multiline regex passes.
5. `array.includes("/")` and `array.includes("..")` test for exact array elements, so the substring traversal is not detected.
6. `path.join("team", array + ".png")` coerces the array to a string, normalises the traversal, and appends `.png`.
7. `slice(0, 100)` truncates the path so the forced `.png` suffix falls after byte 100.
8. Shape the traversal so the joined path is exactly 100 characters ending at the flag file, using `/proc/self/root` and `/proc/thread-self/root` links to pad the length while resolving back to the root.
9. The final request reads `/flag.txt`; the body is the flag even though the content type is `image/png`.

Final path component:

```
../../../../proc/thread-self/root/proc/thread-self/root/proc/self/root/proc/self/root/proc/self/root/flag.txt
```

## Reusable

- A Node API route that validates `query.id` as a string is bypassable with duplicate parameters, because the query value becomes an array.
- `/^[0-9]+$/m` validates one line of a comma-joined array, not the whole value.
- `Array.prototype.includes` checks exact elements, so it misses substring traversal in an array.
- `path.join` normalises traversal; a fixed-length `slice` can remove a forced suffix.

## Traps

- Direct `id=../../...` is rejected; the array form is required.
- `path.join` prefixes `team/`; the traversal must climb out of it.
- The `.png` suffix must land past the 100-character cutoff; use `/proc/self/root` style links to pad.
- The response content type is `image/png` even when the body is text; read the raw body, not an image decoder.
