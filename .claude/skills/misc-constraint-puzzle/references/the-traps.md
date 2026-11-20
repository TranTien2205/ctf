# The traps

- One recv() treated as one message.
- A guessed terminator desyncing every round.
- Format drift in late rounds read as a math bug.
- Optimizing speed before one round works.
