# Chain integrity — the byte check


Every qword must arrive intact — a mangled byte (a bad-byte in an
address, a truncation) breaks the walk at that qword.

## The verify

Echo-check: the service's echo of the input (if any) shows the
arrived bytes.
