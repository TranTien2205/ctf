# Half a question — the partial read

A recv() boundary can split mid-token — `1 23` arrives as `1` then
` 23`. Buffer-until-terminator absorbs it; parsing each recv()
directly desyncs.

## Mid-token splits

until() absorbs partial reads.

## Mid-token

until() absorbs splits.
