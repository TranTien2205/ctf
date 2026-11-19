# The check order — verifying the chain


1. The overwrite lands (rip = your first gadget).
2. Each pop sets its register.
3. The call target is reached.
4. The call's args are right.
5. The call's behavior is observable.

Bisect at the first failing check.
