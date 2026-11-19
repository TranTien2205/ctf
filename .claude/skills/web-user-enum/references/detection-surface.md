# Detection surface — the auth surface's oracle topology

## The surface map

```
entry page
├── /login          (text · status · timing · side · lock)
├── /register       (taken-text · 409 · timing)
├── /forgot-password (send-side · timing · field)
├── /forgot-username (sent-side · timing)
├── /unlock|/reactivate (unlocked vs no-locked)
├── /check-username|/available|/user-exists  (direct boolean)
├── /invite|/contact     (already-member)
├── /mfa|/2fa|/send-otp  (code-sent · timing)
├── /api/login|/token|/auth (JSON error-code/boolean · status)
├── /api/users/{id}      (200/404 — enum + idor)
└── /graphql             (userByEmail/checkUser/login typed errors)
```

## The cheapest-leak path

`check-username` (direct, unauth) → `register` (built to reveal) →
`reset`/`forgot-username` (send side-effect) → `login` (hardened) →
`mfa`/`api` (typed errors).

## The surface-vs-form note

A "surface" is the technology (HTML form, JSON API, GraphQL, REST,
basic-auth, WS); a "form" is the account-touching function (login,
register, reset). Each surface carries each form — probe the matrix,
not just the headline `/login`.

## The coverage rule

A surface is closed only when every form ON it is measured; a form is
closed only when every channel ON it is measured. The full coverage
matrix is `per-form.md` × `per-channel.md`.
