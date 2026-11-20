# The traps

- Timezone assumption — check the log's zone first.
- One line without context — read the window.
- Single-file baseline — read rotated siblings.
- Wrong column — the format's field positions differ.
- Quoted fields split by positional awk — regex-cut referer/UA.
- A count without the denominator — always pair it.
- Grepping a binary/compressed log — zgrep or convert first.
