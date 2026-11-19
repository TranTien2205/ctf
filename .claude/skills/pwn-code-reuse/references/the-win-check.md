# Checking the win function — before using it


A "win" function may not do what its name says — disassemble it
first:

    r2 -A ./chal ; pdf @ win

Does it print a flag? exec a shell? Read a file? Verify the behavior
before chaining to it.
