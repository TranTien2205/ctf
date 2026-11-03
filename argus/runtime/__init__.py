"""The harness plane: one agent loop, one profile per model, one provider per API.

A general harness runs every model the same way, and pays for it twice: the
strong model is held back by caps it does not need, and the weak one drifts
because nothing restates the rules often enough. The profile is where those
differences live — steps, observation size, how often the contract is repeated,
whether several tool calls in one turn are safe — so the loop itself stays one
piece of code.
"""
