# The argv/env layout — predicting stack contents — case catalogue

argv and env sit at the top of the stack: the first bytes a main() frame sees. Their layout predicts what the uninitialized-read leaks and where your shellcode/string can live.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | an env var holds your string | env region address needed | predictable offset |
| 2 | uninit read leaks argv/env pointers | stack-pointer leak | the layout |
| 3 | a string must live at a known address | env or argv region | the layout |

## Falsifier

Falsifier — the environment layout differs from the assumed model (different argv, stripped env): the predicted address is wrong; re-derive it.
