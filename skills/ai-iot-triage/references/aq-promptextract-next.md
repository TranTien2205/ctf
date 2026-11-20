# AI attack cell: prompt-extract / next

Routing module for `ai-iot-triage`. AI and IoT share nothing but the label - this file names the sub-type and the router that owns it; it never solves.

Whether the `prompt-extract` family applies on the
observed model/agent surface for the `next` question - its
precondition, the evidence it produces, and its cost rank
against the other families.

## Order

Families run in cost order; a family whose precondition is
absent is skipped, not retried.
