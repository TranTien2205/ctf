# The metadata workflow — read ALL of it

A media/document file is the handout; the question is a fact about
it — where, when, on what device, or what was inside before it was
shared.

## The order

1. Read ALL metadata: `meta_read.py <file>` (stdlib) or
   `exiftool -a -u -g1 <file>` — the answer is often in an odd
   corner (ThumbnailImage, HistoryParameters, a software string).
2. carve_scan.py + binwalk + strings — appended/embedded data
   the tags never show.
3. The embedded thumbnail — survives edits the main image doesn't.
4. Document revision/author fields — identity + history.

Confirmation is the fact read verbatim — a guess about a GPS
coordinate is a hypothesis until a map source confirms it.
