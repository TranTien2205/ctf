# recv of 0 — the server closed

`recv` returning b'' means the server closed — raise with the
buffered remainder so the log keeps the last bytes seen.

## Closed

b'' = EOF — raise with the remainder.

## Closed

b'' raises with the remainder.
