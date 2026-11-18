# Second-Order XXE — the entity fires somewhere else

## The shape — store XML, parse later

The endpoint that accepts your XML is not where it gets parsed — a
queue worker, a report generator, a nightly importer, an admin viewer —
the entity substitution happens in a different process, often with more
privilege or different egress.

## The trigger patterns

- **Import → process** — upload XML to a queue; a worker parses it
- **Store → render** — an XML config stored, rendered into an admin page
- **Draft → publish** — an XML draft, parsed when "published"
- **Batch → report** — XML rows batched, a report job parses
- **Stage → deploy** — XML config staged, deployed by a different service
- **User → admin** — user submits XML that the admin's viewer parses —
  the parse runs with ADMIN rights

## The evidence problem — the response is not the answer

The request that stores the XML returns 200/created — the entity
substitution happens LATER, in a different response (the report, the
admin view) or not at all visibly (blind OOB). You must:

1. Identify where the parse happens (source trace, or the feature that
   "shows the result")
2. Watch the right surface — the report, the admin page, the OOB listener
3. Time the trigger — the parse may be cron-driven — poll

## The classic CTF shape — "upload a config, admin reviews it"

```
POST /config     {"xml": "<!DOCTYPE...><r>&x;</r>"}   → 200, stored
GET  /admin/configs  — admin view shows substituted &x;
```

The admin's viewer has different parsing (maybe different hardening) —
the user's path may be sanitized, the admin path live.

## The email/SAML/order-import family

- order import (`orders.xml` → fulfillment)
- invoice upload (`invoice.xml` → billing)
- SAML IdP onboarding (metadata URL → parsed by the app)
- webhook/XML payload → the receiver parses later

## The OOB twist — second-order blind

The entity fires in a worker with network access — the OOB listener
sees the hit even when the original requester sees nothing — the
canary proves it was YOUR stored XML that fired.

## The evidence chain

- the store-request's response (the stored ID)
- the delayed response (the report/admin view) OR the OOB hit
- the gap between them — the "which process parsed it" signal

## Falsifiers

- the parse never fires (feature disabled, no worker) → no second-order
- the worker is hardened → dead
