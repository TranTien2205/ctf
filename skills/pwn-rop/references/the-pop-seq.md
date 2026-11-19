# The pop sequence — ordering the setters


Order pops so later gadgets don't clobber set registers: a pop with
a side effect goes FIRST (before the register it clobbers is set);
the last pop is adjacent to the call.
