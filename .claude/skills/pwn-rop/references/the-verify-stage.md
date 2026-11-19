# The staged verify — test before firing


Don't fire the whole chain blind:

1. Send the offset-padding alone — confirm the overwrite lands
   (the crash's rip = your control value or the first gadget).
2. Send through the first gadget — confirm rip lands there.
3. Add the call — confirm the observable.

## The rule

Each stage's failure is isolated before it compounds.
