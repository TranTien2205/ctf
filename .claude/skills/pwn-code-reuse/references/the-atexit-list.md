# The atexit list — the exit hook chain


Functions registered via atexit run at exit — the internal list is a
writable structure; a forged entry fires at exit.

## The shape

The list lives in libc's data — needs a libc leak + a write; a
__free_hook-class target.
