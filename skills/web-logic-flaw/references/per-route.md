# Per-route map — which mechanisms live on which endpoint shapes

## `/register`, `/signup`, `/users` (POST)

- **mass assignment** — the canonical home. Every model field not on the
  form is a probe: `role`, `balance`, `verified`, `permissions`, `plan`.
- **role assignment** — same mechanism, higher stakes reading.
- **singleton** — a second `admin`/`root` account if uniqueness is
  only on username.
- Probe shape: `POST` with the extra field → `GET` the object → diff.

## `/login`, `/session`

- **time assumption** — token expiry in client reach.
- **sequence** — session IDs from a predictable counter.
- Usually auth-session's ground — route when the bug is "who the session
  is" not "what order it may act".

## `/cart`, `/basket`, `/order` (POST/PUT)

- **numeric boundary** — `quantity`, `price`, `discount` — the boundary
  alphabet's home field.
- **unit confusion** — cents vs dollars on `price`/`amount`.
- **ownership** — `cartId`/`orderId` of another user (IDOR boundary).
- **trust-in-earlier-step** — `price`/`total` carried in the request.

## `/checkout`, `/pay`, `/confirm`, `/complete`

- **workflow skip** — the terminal action without the payment step.
- **state replay** — double-confirm, double-charge.
- **trust-in-earlier-step** — `total`/`amount` echoed from earlier steps.
- The verbatim forbidden state: `"status":"confirmed"` AND
  `"charged":0` (or `paid:false`).

## `/redeem`, `/coupon`, `/claim`, `/vote`, `/refund`

- **idempotency** — the one-time action's home.
- **state replay** — serial double-apply.
- **sequence** — replaying codes/IDs in order.
- **time** — expired codes still redeemable.
- Cross-user replay: code consumed by A, replayed by B.

## `/verify`, `/activate`, `/reset`

- **workflow skip** — activation without verification.
- **state replay** — reset token reuse.
- **time** — expired token acceptance.
- **sequence** — token predictability.

## `/admin`, `/flag`, `/download`, `/export`

- **workflow skip** — terminal endpoint bare — does it check ANY state?
- **role** — reached only via a privileged field from an earlier bug.
- These are usually the SINK — what the chain reaches, not where the
  mechanism lives.

## `/update`, `/edit`, `/profile` (PATCH/PUT)

- **mass assignment** — a second, often wider binder than `register`.
- **ownership** — updating another user's object.
- **trust** — `role`-shaped fields the profile form doesn't render.

## `/transfer`, `/withdraw`, `/deposit`

- **idempotency** — double-apply the transfer.
- **numeric boundary** — negative transfer (a "withdrawal" of `-100` is
  a deposit), zero, NaN.
- **ownership** — `from` account of another user.
- **sequence** — replaying a transfer nonce.

## `/api/*` machine endpoints

- Same mechanisms, but: JSON body conventions open the object/array
  variants (`{"role":["admin"]}`, `{"user":{"role":"admin"}}`), and
  `additionalProperties` schemas decide mass assignment.

## Anything taking an index/offset into a shared structure

- **scaling-after-check** — the Pachinko shape. Emulators, interpreters,
  file offsets, record IDs that get transformed. Map the checker's bound
  vs the transform's reach.
