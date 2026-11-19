# Theory — why mass assignment exists and why it survives audits

## The abstraction leak

Frameworks bind request input to model objects to save the developer
from hand-writing `user.name = params[:name]` per field. The binding is
meant to be *convenient* — and convenience means *coverage*: bind
everything, let the developer subtract the dangerous fields. Mass
assignment is the subtraction never happening.

## The three security models

| Model | Default | Failure mode |
|---|---|---|
| bind-all-then-subtract | everything binds; developer allowlists | the allowlist is forgotten or wrong |
| allowlist-then-bind | nothing binds unless declared | the declared set includes a dangerous field |
| schema-first | the schema IS the model | the schema validates types, not field admission |

Every mass-assignment bug is one of: the subtract-list forgotten, the
declared-set too wide, or the schema checking types not admission.

## Why it survives code review

- The dangerous field doesn't LOOK dangerous — `role` is a normal
  column; the risk is that it exists on the writable surface at all.
- The allowlist is per-endpoint — register whitelists `[u,p]`, PATCH
  whitelists `[name,bio,role]` — and the reviewer sees each in
  isolation, not the union.
- The second binder is invisible — `PATCH /users/me` uses a different
  code path than `POST /register`; the reviewer checks the create form.
- Type-coercion hides the semantic — `role:"admin"` looks like a string;
  the column is an enum where `1` = admin.

## The defense depth

| Layer | Defense | The gap |
|---|---|---|
| client | JS builds only declared fields | the wire isn't the client |
| proxy | param allowlist | content-type shift; nested; dupes |
| schema | `additionalProperties:false` | form path uses a different parser |
| binder | `permit`/`$fillable`/`pick` | nested under allowed parent; second binder |
| model | `attr_protected`/`readonly` | nested association reaches through |
| store | column permissions | rarely used; the app owns all columns |

Every layer's fix is a *subtraction* — and subtraction is what the
developer forgot.

## The reach graph

A bound field's risk is the set of decisions that READ it. `role` is
riskless if nothing reads it; it's critical if `check_admin()` reads
`user.role`. The field inventory + the decision map = the reach graph;
the exploit is the shortest path from a bindable field to a gated
decision.

## The second-order problem

The bound field may not grant privilege directly — it enables a SECOND
binder. `role:admin` → `/admin/users` → the admin endpoint's own mass-
assignment (`flag_visible:true`). The reach graph includes edges where
the bound field unlocks a wider binder.

## Why the falsifier depth matters

A falsifier isn't "the class is dead" — it's "this cell is dead." The
binder allowlist at `POST /register` says nothing about `PATCH` —
different code, different list. The class is dead only when the MODEL
carries no privileged fields, or when EVERY binder is allowlisted.
Depth-annotated falsifiers are the honest map.
