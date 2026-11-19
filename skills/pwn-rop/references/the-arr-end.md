# The array's end — the NULL sentinel


argv and envp are NULL-terminated pointer arrays — the sentinel
qword of 0 ends them; a missing sentinel runs the walk into garbage.
