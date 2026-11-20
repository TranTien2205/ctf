# Batching — pipeline when allowed

If the protocol accepts answers without a prompt-per-question, send
the batch and drain — but only after the serial form works; a
half-open pipeline desyncs the framing.

## Serial first

Pipeline only after the serial form passes.

## Serial first

Pipeline only after serial passes.
