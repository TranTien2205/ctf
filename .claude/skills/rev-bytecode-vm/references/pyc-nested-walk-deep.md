# Walking nested code objects — deep

Companion to `pyc-nested-walk.md`.

Module code's co_consts nests function/class/lambda code objects — the check lives in one of them. Recurse: `for c in co_consts: if hasattr(c,'co_code'): dis.dis(c)`.
