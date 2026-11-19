# x86 cdecl deep — the stack args


Args push right-to-left; the caller cleans up — the chain's layout
[func][ret][arg0][arg1] supplies them; the ret is the callee's return
target.
