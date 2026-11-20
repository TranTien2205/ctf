# Evidence — what counts

- The reassembled stream/object bytes carrying the flag.
- The protocol + the field/stream that carried it.
- The flag through hooks.py pre-flag.

A "this protocol looks odd" is a lead.

## The stronger record

- The capture's format + linktype.
- The protocol + the flow/stream/field that carried it.
- The reassembly order + the decode applied.
- The reassembled bytes quoted verbatim.

## What is NOT evidence

- A filter result that looks interesting.
- A single packet's field.
- A strings hit on the raw capture that was never reassembled.
- An exported object never opened.
- A "the flag is probably chunked" without the reassembly.
