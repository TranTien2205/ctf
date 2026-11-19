# Mechanism index — the mass-assignment mechanism catalogue

| # | Mechanism | The bug | Detection | Falsifier |
|---|---|---|---|---|
| A | merge-all binder | no allowlist | extras land flat | model/check-set |
| B | kwargs signature | signature too wide | `TypeError` on unknown | field not in signature |
| C | allowlist | declared set too wide | nested survives | nested also dropped |
| D | strict schema | parser kills extras | `400`/`422` | all carriers reject |
| E | deep merge | nested tunnel | nested survives flat-drop | depth-2 also dropped |
| F | nested association | child model reachable | `profile`/`membership` binds | assoc key rejected |
| G | discriminator | schema switch | `_t`/`type` binds | discriminator readonly |
| H | type coercion | wrong-type fails | `500`/`400` on type | right-type also fails |
| I | method permutation | binder per method | PATCH lands, POST drops | all methods drop |
| J | serializer-hidden | store ≠ response | decision proves, GET blind | decision also unchanged |

## The mechanism-to-probe map

| Mechanism | First probe | The tunnel |
|---|---|---|
| A | `role` flat | none needed |
| B | `role` flat → `TypeError` | the signature's own fields |
| C | `role` flat → drop | `{"profile":{"role":..}}` |
| D | `role` flat → `400` | form carrier |
| E | `{"profile":{"role":..}}` | depth-2 `{"a":{"b":{"role":..}}}` |
| F | `{"membership":{"role":..}}` | `role_ids[]` |
| G | `{"_t":"AdminUser"}` | `type`/`__t` variants |
| H | `role:true` → `400` | `role:"admin"`, `role:1` |
| I | `PATCH` vs `POST` `role` | `PUT`, `?_method` |
| J | `role` → exercise directly | a second representation |

## The mechanism-to-budget map

5 probes per mechanism cell:

1. `role` flat on the widest endpoint;
2. `{"profile":{"role":..}}` nested;
3. `role` on a second carrier (form if JSON dropped);
4. a second semantic (`verified`/`balance`);
5. a typed variant (`role:1`, `groups:[{id:1}]`).

A falsifier at any mechanism closes the cell; the remaining cells are
the falsifier's "open" column.
