# Onboarding — mass assignment for a first-time reader

## The one-paragraph version

The web framework maps your request's fields into a database object.
If it maps fields you never declared — `role`, `is_admin`, `balance` —
you can write privilege into your account. The test is: send the extra
field, then READ the object back through a different endpoint — if it
stored AND changes a decision (an admin route opens), it's real.

## The mental model

Think of the model as a table row with columns the form never shows:
`role`, `verified`, `balance`, `plan`. The form fills `username` and
`password`; the binder fills whatever the request contains. Send
`{"username":"x","role":"admin"}` and the `role` column may fill too.

## The first five minutes

1. `GET /api/me` — every key the response returns is a candidate
   writable field;
2. `PATCH /users/me {"role":"admin"}` — the update binder is the
   widest; send the extra field;
3. `GET /api/me` again — did `role` land?
4. `GET /admin` — did the gate open?

## The two things that can go wrong

- **The field drops** — the binder has an allowlist; the read-back
  shows the control state. Try `{"profile":{"role":..}}` nested, the
  form carrier, or a different endpoint.
- **The field stores but does nothing** — `role:"admin"` lands but
  `/admin` still `403`s — the gate reads `is_staff` instead. Find the
  gate's real field.

## The honest-null rule

A stored field that changes nothing is a NULL result — record it,
don't cite it. The finding is the CHANGED DECISION, not the stored
bytes.

## The one tool

```bash
python3 tools/web/binding_probe.py --url "$BASE/api/register" \
  --body 'username=p&password=x' --readback "$BASE/api/me"
```

It sends the common field set (`role`, `admin`, `is_admin`, `debug`,
`permissions`, `group`, `verified`, `is_staff`) and grades echo vs
landed.
