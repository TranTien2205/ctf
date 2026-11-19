# Detection index — the business-logic artifacts that name the mechanism, indexed

The index is the lookup — the artifact, the mechanism, the probe, the
confirmation, the falsifier.

## The artifact index

| Artifact | Mechanism | Probe | Confirmation | Falsifier |
|---|---|---|---|---|
| `role` in register body | mass assignment | `register` with `role=admin` | `role: admin` in read-back | `role: user` or `400` |
| `isAdmin`/`is_admin`/`admin` in register body | mass assignment | `register` with the field | `admin` in read-back | `user` or `400` |
| `balance`/`credits`/`wallet` in register body | mass assignment | `register` with the field | `balance: 1000000` in read-back | `balance: 0` or `400` |
| `verified`/`isVerified`/`is_verified` in register body | mass assignment | `register` with the field | `verified: true` in read-back | `verified: false` or `400` |
| `permissions`/`groups`/`scope` in register body | mass assignment | `register` with the field | `permissions: admin` in read-back | `permissions: user` or `400` |
| `plan`/`tier`/`subscription` in register body | mass assignment | `register` with the field | `plan: pro` in read-back | `plan: free` or `400` |
| `flags` in register body | mass assignment | `register` with the field | `flags: FLAG` in read-back | `flags: none` or `400` |
| `owner`/`ownerId`/`userId` in register body | mass assignment | `register` with the field | `owner: attacker` in read-back | `owner: user` or `400` |
| `__proto__`/`constructor` in register body | mass assignment | `register` with the field | `role: admin` in read-back | `role: user` or `400` |
| `step`/`state`/`token` in workflow | workflow skip | call the later step | `200` + forbidden state | `400`/`302` to earlier step |
| `orderId`/`cartId`/`token` in workflow | workflow skip | call the later step | `200` + forbidden state | `400`/`302` to earlier step |
| `code`/`token`/`nonce` in replay | state replay | replay the transition | same effect twice | `400`/`409` |
| `quantity`/`price`/`amount` in arithmetic | numeric boundary | send the forbidden value | forbidden state reached | `400`/`clamp` |
| `discount`/`coupon`/`rate` in arithmetic | numeric boundary | send the forbidden value | forbidden state reached | `400`/`clamp` |
| `index`/`offset`/`id` in scaling | scaling-after-check | pick the index | transformed address out of range | `400`/`clamp` |
| `unit`/`currency`/`amount` in unit confusion | unit confusion | send the other unit | forbidden state reached | `400`/`clamp` |
| `role`/`permissions`/`scope` in registration | role assignment | register with the field | `role: admin` in read-back | `role: user` or `400` |
| `refund`/`cancel`/`redeem` in idempotency | idempotency | replay the action | same effect twice | `400`/`409` |
| `transfer`/`withdraw`/`deposit` in idempotency | idempotency | replay the action | same effect twice | `400`/`409` |
| `invite`/`refer`/`claim` in idempotency | idempotency | replay the action | same effect twice | `400`/`409` |
| `createdAt`/`expiry`/`timestamp` in time | time assumption | send the past/future time | forbidden state reached | `400`/`clamp` |
| `sequence`/`nonce`/`id` in sequence | sequence assumption | replay an old ID | forbidden state reached | `400`/`409` |
| `objectId`/`recordId`/`docId` in ownership | ownership assumption | reference another user's object | forbidden state reached | `400`/`403` |
| `singleton`/`admin`/`flag` in singleton | singleton assumption | create a second privileged object | forbidden state reached | `400`/`409` |
| `price`/`total`/`discount` in echo-back | trust-in-earlier-step | modify the upstream value | forbidden state reached | `400`/`400` |
| `state`/`token`/`flag` in stored-state | trust-in-earlier-step | modify the upstream value | forbidden state reached | `400`/`400` |
| `header`/`Referer`/`Origin` in header-trust | trust-in-earlier-step | modify the header | forbidden state reached | `400`/`403` |

## The mechanism index

| Mechanism | Artifacts | The probe |
|---|---|---|
| mass assignment | `role`/`isAdmin`/`balance`/`verified`/`permissions`/`plan`/`flags`/`owner`/`__proto__` in register body | `register` with the field |
| workflow skip | `step`/`state`/`token`/`orderId`/`cartId` in workflow | call the later step |
| state replay | `code`/`token`/`nonce` in replay | replay the transition |
| numeric boundary | `quantity`/`price`/`amount`/`discount`/`coupon`/`rate` in arithmetic | send the forbidden value |
| scaling-after-check | `index`/`offset`/`id` in scaling | pick the index |
| unit confusion | `unit`/`currency`/`amount` in unit confusion | send the other unit |
| role assignment | `role`/`permissions`/`scope` in registration | register with the field |
| idempotency | `refund`/`cancel`/`redeem`/`transfer`/`withdraw`/`deposit`/`invite`/`refer`/`claim` in idempotency | replay the action |
| time assumption | `createdAt`/`expiry`/`timestamp` in time | send the past/future time |
| sequence assumption | `sequence`/`nonce`/`id` in sequence | replay an old ID |
| ownership assumption | `objectId`/`recordId`/`docId` in ownership | reference another user's object |
| singleton assumption | `singleton`/`admin`/`flag` in singleton | create a second privileged object |
| trust-in-earlier-step | `price`/`total`/`discount`/`state`/`token`/`flag`/`header`/`Referer`/`Origin` in echo-back | modify the upstream value |
