# Business-logic flaws

**When:** the app enforces rules in the client, trusts state it gave you,
or lets steps be skipped/replayed. No signature pattern - this is why
scanners miss it and agents find it.

## The five durable patterns

1. **Client-side enforcement** - price, quantity, role, `hidden` fields
   sent back to server and trusted. Change them: `price=-100`,
   `quantity=-5` (negative refund), `role=admin` on register/update.
2. **Step skipping** - multi-step flows (checkout, KYC, reset): request
   step 3 without step 2; visit the "confirm" URL directly; POST the final
   action with a token from an earlier stage.
3. **Replay** - reuse a one-time token/link/coupon; submit the same
   transaction twice; refresh the success page (see `race-condition` for
   the concurrent variant).
4. **Parameter tampering** - ids and amounts in the URL/body of a POST
   that the page never exposed; also mass-assignment of undeclared fields.
5. **Trust boundaries between subsystems** - cart total computed on the
   front-end; discount applied twice; currency conversion in your favor;
   email verified only on one service.

## Method

- Read the flow end-to-end FIRST (crawl + a manual walk via http_request):
  every step, every token, every state transition. Most logic bugs are
  visible in the design before you send a payload.
- For each state transition ask: who could send this, with what, out of
  order, twice, or with values from a different object/account?
- One extra field at a time in JSON bodies; one skipped step at a time.

## Proof standard

The finding needs the RESULT: account shows the forged role, order totals
change, the skipped step's protection never ran. A suspicious field that
does nothing is a note.

## Falsifier

Extra fields are ignored, out-of-order requests are rejected with the
correct error, replays return "already used". Write that in notes.

## Severity guide

Financial manipulation / privilege gain / auth bypass via flow: high-critical.
Abuse requiring victim action or bounded gain: medium. Weird-but-harmless
state: low-info.
