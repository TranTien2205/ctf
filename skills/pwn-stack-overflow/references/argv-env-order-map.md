# The argv/env layout — predicting stack contents — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| an env var holds your string | env region address needed | predictable offset |
| uninit read leaks argv/env pointers | stack-pointer leak | the layout |
| a string must live at a known address | env or argv region | the layout |

## Falsifier

Falsifier — the environment layout differs from the assumed model (different argv, stripped env): the predicted address is wrong; re-derive it.
