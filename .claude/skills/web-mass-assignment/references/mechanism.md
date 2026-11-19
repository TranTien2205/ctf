# Mechanism — how mass assignment actually works

Mass assignment is a binder-layer bug: the framework maps request input
into a model object, and the mapping's coverage exceeds the form's
declared fields. This module is the mechanism's anatomy — the code
paths, the merge semantics, and the exact points where extra fields
become stored attributes.

## The pipeline

```
request body (JSON/form/query)
    → parser (body → object)
    → binder (object → model instance)
    → model.save() (instance → store)
    → serializer (instance → response representation)
```

The bug lives between parser and save: `binder(req.body)` copies keys
the form never declared into model attributes. Three sub-mechanisms
decide whether an extra field lands:

1. **coverage** — which keys the binder copies (all vs allowlist);
2. **depth** — flat keys only vs recursive merge into nested objects;
3. **persistence** — the field reaching the stored record vs dropped
   at serialization.

## The merge semantics per binder family

| Family | Default behavior | The allowlist |
|---|---|---|
| merge-all | every key in body → `setattr`/property set | `pick(body, [...])`, `permit(...)`, `$fillable`, `[Bind(Include)]`, `fields=` |
| constructor-kwargs | `Model(**body)` — TypeError on unknown keys | the kwargs signature IS the schema |
| deserialize-then-bind | deserializer drops unknowns (`strict` schema) | schema's `additionalProperties` / `strict` |
| explicit-update | `Object.assign(model, body)` / `model.update(body)` | a `fields` option or manual whitelist |

## The three-layer decision

A probe field can die at three layers — each produces a different
negative:

| Layer | Death shape | Reading |
|---|---|---|
| parser | `400` on unknown key (strict schema, `additionalProperties:false`) | schema falsifier — this content-type dead |
| binder | `200` + field absent in read-back | allowlist/drop — the binder ignored it |
| serializer | `200` + field stored but never returned/decision-relevant | null result — recorded, not cited |

## The merge directions

- **Shallow merge**: `{...model, ...body}` — only top-level keys
  contest. `{"user":{"role":...}}` replaces `user` wholesale or merges
  one level — the binder's depth decides.
- **Deep merge**: recursive walk — `{"billing":{"price":0}}` writes
  `billing.price` inside the existing object. PATCH handlers are the
  classic deep-merge site.
- **Replace**: `PUT` semantics — the body REPLACES the object; extra
  fields bind only if the model accepts them, but omitted fields reset
  to defaults (a different footgun — the wipe).

## Where the extra field comes from

The binder doesn't know what the "form" sends — it binds what the
REQUEST sends. The attacker adds keys the client's form never renders:

- JSON: `{"username":"x","role":"admin"}`;
- form: `username=x&role=admin`;
- nested: `{"user":{"role":"admin"}}`, `user[role]=admin`;
- array: `{"role":["admin"]}`, `role[]=admin`;
- duplicate: `role=user&role=admin` (first-vs-last parser semantics);
- dotted: `user.role=admin` (qs-style nesting).

## The persistence question

A bound field must SURVIVE to the store to matter. Two silent drops:

- `strict` schema (Mongoose default): unknown keys set on the instance
  but `save()` persists only schema paths — the echo can show `role`
  while the store never gets it;
- serializer allowlist (`toJSON`/`as_json`/`fields=`): the store holds
  the field but no response ever shows it — the field is bound, stored,
  and invisible. The read-back through a DIFFERENT representation
  (`/api/me` vs the write echo) is what detects it.

## The decision test — what makes it a finding

The class bar, verbatim from SKILL.md: **a stored field that is never
read anywhere is not a finding**. The bound field must change a
decision — `role` opening an admin route, `price` flowing into a
checkout total, `verified`/`approved` flipping a gate. The confirm is
always two observations: the field STORED (read-back) AND the decision
CHANGED (the gated endpoint responds differently).

## The boundary with prototype pollution

`constructor.prototype`/`__proto__` keys do not write a field on ONE
object — they write a property on the shared prototype, affecting every
object in the process. That is `web-prototype-pollution`, a different
class with different evidence (pollution observed on a second object,
not the written one). A probe returning "role bound on my account"
is mass assignment; a probe where `{}.role` suddenly exists for
everyone is pollution — route accordingly.
