# The ret-chain end — the final ret


The chain's last ret pops the ending — an exit() call, a loop return,
or a deliberate landing. Without a defined ending, rsp walks into
garbage — usually fine post-flag, cleaner to end deliberately.
